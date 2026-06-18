"""Main entry point for LinkedIn Comment Lead Extractor."""
import asyncio
import sys
from pathlib import Path
from typing import Optional
import click

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import Config
from logging_config import setup_logging, get_logger
from browser import BrowserManager
from authenticator import LinkedInAuthenticator
from extractor import LinkedInCommentExtractor
from exporters import ExportManager
from utils import URLValidator

logger = get_logger(__name__)


class LinkedInExtractorApp:
    """Main application class."""

    def __init__(self):
        """Initialize application."""
        setup_logging()
        self.browser_manager: Optional[BrowserManager] = None

    async def run(
        self,
        post_url: str,
        email: Optional[str] = None,
        password: Optional[str] = None,
        force_login: bool = False,
        export_format: str = "all",
    ) -> bool:
        """Run the extraction pipeline."""
        try:
            # Validate URL
            if not URLValidator.is_valid_linkedin_post_url(post_url):
                logger.error(f"Invalid LinkedIn post URL: {post_url}")
                return False

            # Initialize browser
            self.browser_manager = BrowserManager()
            await self.browser_manager.initialize()

            # Authenticate
            authenticator = LinkedInAuthenticator(self.browser_manager)
            if not await authenticator.login(email, password, force_login):
                logger.error("Failed to authenticate to LinkedIn")
                return False

            # Extract comments
            extractor = LinkedInCommentExtractor(self.browser_manager, post_url)
            comments = await extractor.extract_comments()

            if not comments:
                logger.warning("No comments extracted from post")
                return False

            # Remove duplicates
            extractor.remove_duplicates()

            # Convert to dict for export
            comment_dicts = [comment.to_dict() for comment in extractor.comments]

            # Export data
            export_manager = ExportManager(comment_dicts)

            if export_format == "all":
                results = export_manager.export_all()
            else:
                success = export_manager.export_to_format(export_format)
                results = {export_format: success}

            logger.info(f"Export results: {results}")

            return all(results.values())

        except Exception as e:
            logger.error(f"Application error: {str(e)}")
            return False

        finally:
            if self.browser_manager:
                await self.browser_manager.close()

    @staticmethod
    def run_sync(
        post_url: str,
        email: Optional[str] = None,
        password: Optional[str] = None,
        force_login: bool = False,
        export_format: str = "all",
    ) -> bool:
        """Run synchronously."""
        app = LinkedInExtractorApp()
        return asyncio.run(
            app.run(post_url, email, password, force_login, export_format)
        )


@click.group()
def cli() -> None:
    """LinkedIn Comment Lead Extractor CLI."""
    pass


@cli.command()
@click.option(
    "--url",
    required=True,
    help="LinkedIn post URL",
    prompt="Enter LinkedIn post URL",
)
@click.option(
    "--email",
    default=None,
    help="LinkedIn email (uses .env if not provided)",
)
@click.option(
    "--password",
    default=None,
    help="LinkedIn password (uses .env if not provided)",
)
@click.option(
    "--force-login",
    is_flag=True,
    help="Force login even if cookies exist",
)
@click.option(
    "--format",
    "export_format",
    type=click.Choice(["csv", "excel", "gsheets", "all"]),
    default="all",
    help="Export format",
)
def extract(
    url: str,
    email: Optional[str],
    password: Optional[str],
    force_login: bool,
    export_format: str,
) -> None:
    """Extract comments from a LinkedIn post."""
    logger_instance = get_logger(__name__)

    if not Config.validate():
        logger_instance.error(
            "LinkedIn credentials not configured. Set LINKEDIN_EMAIL and LINKEDIN_PASSWORD in .env"
        )
        sys.exit(1)

    logger_instance.info(f"Starting extraction from {url}")

    success = LinkedInExtractorApp.run_sync(
        post_url=url,
        email=email,
        password=password,
        force_login=force_login,
        export_format=export_format,
    )

    if success:
        logger_instance.info("Extraction completed successfully")
        click.echo(click.style("✓ Extraction completed successfully!", fg="green"))
        sys.exit(0)
    else:
        logger_instance.error("Extraction failed")
        click.echo(click.style("✗ Extraction failed!", fg="red"))
        sys.exit(1)


@cli.command()
@click.option(
    "--email",
    default=None,
    help="LinkedIn email",
    prompt="Enter LinkedIn email",
)
@click.option(
    "--password",
    default=None,
    help="LinkedIn password",
    prompt="Enter LinkedIn password",
    hide_input=True,
)
def login(email: str, password: str) -> None:
    """Test LinkedIn login."""
    logger_instance = get_logger(__name__)

    async def _login():
        browser_manager = BrowserManager()
        try:
            await browser_manager.initialize()
            authenticator = LinkedInAuthenticator(browser_manager)
            success = await authenticator.login(email, password)

            if success:
                logger_instance.info("Login successful")
                click.echo(click.style("✓ Login successful!", fg="green"))
            else:
                logger_instance.error("Login failed")
                click.echo(click.style("✗ Login failed!", fg="red"))

        finally:
            await browser_manager.close()

    asyncio.run(_login())


@cli.command()
def version() -> None:
    """Show version."""
    from __init__ import __version__

    click.echo(f"LinkedIn Comment Lead Extractor v{__version__}")


if __name__ == "__main__":
    cli()
