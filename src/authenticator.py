"""LinkedIn authentication module."""
from typing import Optional
import asyncio

from browser import BrowserManager
from config import Config
from logging_config import get_logger

logger = get_logger(__name__)


class LinkedInAuthenticator:
    """Handles LinkedIn login and session management."""

    LINKEDIN_LOGIN_URL = "https://www.linkedin.com/login"
    LINKEDIN_HOME_URL = "https://www.linkedin.com/feed/"

    def __init__(self, browser_manager: BrowserManager):
        """Initialize authenticator."""
        self.browser_manager = browser_manager

    async def login(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        force_login: bool = False,
    ) -> bool:
        """Authenticate to LinkedIn."""
        email = email or Config.LINKEDIN_EMAIL
        password = password or Config.LINKEDIN_PASSWORD

        if not email or not password:
            logger.error("LinkedIn credentials not provided")
            return False

        if not force_login and await self._is_logged_in():
            logger.info("Already logged in to LinkedIn")
            return True

        try:
            logger.info("Attempting to login to LinkedIn")
            await self.browser_manager.goto(self.LINKEDIN_LOGIN_URL)

            # Wait for login form
            await asyncio.sleep(2)

            # Enter email
            await self.browser_manager.page.fill(
                'input[aria-label="Email or phone number"]', email
            )
            logger.debug("Email entered")

            # Enter password
            await self.browser_manager.page.fill(
                'input[aria-label="Password"]', password
            )
            logger.debug("Password entered")

            # Click login button
            await self.browser_manager.page.click(
                'button[aria-label="Sign in"]'
            )

            # Wait for login to complete
            await asyncio.sleep(5)

            # Check if login was successful
            if await self._is_logged_in():
                logger.info("Successfully logged in to LinkedIn")
                self.browser_manager.save_cookies()
                return True
            else:
                logger.error("Login failed - verification required or credentials invalid")
                return False

        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False

    async def _is_logged_in(self) -> bool:
        """Check if currently logged in."""
        try:
            await self.browser_manager.goto(self.LINKEDIN_HOME_URL)
            await asyncio.sleep(2)

            # Check if we're on the feed page (logged in)
            current_url = self.browser_manager.page.url
            is_logged_in = "feed" in current_url or "mynetwork" in current_url

            if is_logged_in:
                logger.debug("User is logged in")
            else:
                logger.debug("User is not logged in")

            return is_logged_in

        except Exception as e:
            logger.warning(f"Failed to check login status: {str(e)}")
            return False

    async def logout(self) -> bool:
        """Logout from LinkedIn."""
        try:
            logger.info("Logging out from LinkedIn")
            await self.browser_manager.goto(self.LINKEDIN_HOME_URL)
            await asyncio.sleep(2)

            # Click profile icon
            await self.browser_manager.page.click(
                'button[aria-label="Profile"]'
            )
            await asyncio.sleep(1)

            # Click sign out
            await self.browser_manager.page.click("a:has-text('Sign out')")
            await asyncio.sleep(2)

            logger.info("Logged out successfully")
            return True

        except Exception as e:
            logger.error(f"Logout failed: {str(e)}")
            return False
