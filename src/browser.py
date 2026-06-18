"""Browser management module using Playwright."""

from typing import Optional, Any
from playwright.async_api import (
    async_playwright,
    Browser,
    BrowserContext,
    Page,
)
import json
from pathlib import Path

from config import Config
from logging_config import get_logger

logger = get_logger(__name__)


class BrowserManager:
    """Manages Playwright browser instance and context."""

    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright: Optional[Any] = None

    async def initialize(self) -> None:
        """Initialize browser and context."""

        try:
            self.playwright = await async_playwright().start()

            self.browser = await self.playwright.chromium.launch(
                headless=False,  # IMPORTANT FOR DEBUGGING
                slow_mo=100,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--start-maximized",
                ],
            )

            logger.info("Browser initialized")

            cookies = None

            if Config.USE_SAVED_COOKIES:
                cookies = self._load_cookies()

            self.context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/137.0.0.0 Safari/537.36"
                ),
            )

            if cookies:
                try:
                    await self.context.add_cookies(cookies)
                    logger.info(
                        f"Loaded {len(cookies)} cookies"
                    )
                except Exception as e:
                    logger.warning(
                        f"Failed to load cookies: {e}"
                    )

            self.page = await self.context.new_page()

            logger.info("Page created successfully")

        except Exception as e:
            logger.error(
                f"Failed to initialize browser: {e}"
            )
            raise

    async def close(self) -> None:
        """Close browser."""

        try:
            if self.page:
                await self.page.close()

            if self.context:
                await self.context.close()

            if self.browser:
                await self.browser.close()

            if self.playwright:
                await self.playwright.stop()

            logger.info("Browser closed successfully")

        except Exception as e:
            logger.error(
                f"Error closing browser: {e}"
            )

    def _load_cookies(self) -> Optional[list]:
        """Load cookies."""

        session_file = Config.get_session_file()

        try:
            if session_file.exists():
                with open(session_file, "r", encoding="utf-8") as f:
                    return json.load(f)

        except Exception as e:
            logger.warning(
                f"Failed to load cookies: {e}"
            )

        return None

    async def save_cookies(self) -> None:
        """Save cookies."""

        if not self.context:
            return

        try:
            cookies = await self.context.cookies()

            session_file = Config.get_session_file()

            with open(
                session_file,
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(
                    cookies,
                    f,
                    indent=2,
                )

            logger.info(
                f"Saved {len(cookies)} cookies"
            )

        except Exception as e:
            logger.error(
                f"Failed to save cookies: {e}"
            )

    async def goto(self, url: str) -> None:
        """Navigate to URL."""

        if not self.page:
            raise RuntimeError(
                "Page not initialized"
            )

        try:
            await self.page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=60000,
            )

            logger.info(
                f"Navigated to {url}"
            )

        except Exception as e:
            logger.error(
                f"Failed to navigate to {url}: {e}"
            )
            raise

    async def wait_for_selector(
        self,
        selector: str,
        timeout: int = 10000,
    ) -> bool:
        """Wait for selector."""

        if not self.page:
            raise RuntimeError(
                "Page not initialized"
            )

        try:
            await self.page.wait_for_selector(
                selector,
                timeout=timeout,
            )

            return True

        except Exception:
            logger.warning(
                f"Selector not found: {selector}"
            )
            return False

    async def scroll_page(
        self,
        scroll_amount: int = 1000,
    ) -> None:
        """Scroll page."""

        if not self.page:
            raise RuntimeError(
                "Page not initialized"
            )

        await self.page.evaluate(
            f"window.scrollBy(0, {scroll_amount})"
        )

    async def get_page_height(self) -> int:
        """Get page height."""

        if not self.page:
            raise RuntimeError(
                "Page not initialized"
            )

        return await self.page.evaluate(
            "document.body.scrollHeight"
        )

    async def get_inner_html(
        self,
        selector: str,
    ) -> Optional[str]:
        """Get element HTML."""

        if not self.page:
            raise RuntimeError(
                "Page not initialized"
            )

        try:
            return await self.page.inner_html(
                selector
            )

        except Exception as e:
            logger.error(
                f"Failed to get HTML: {e}"
            )
            return None