"""LinkedIn comment extraction module."""

from typing import List, Dict, Any, Optional
import asyncio

from bs4 import BeautifulSoup

from browser import BrowserManager
from email_parser import EmailParser
from utils import URLValidator, DataCleaner, DateTimeHelper
from config import Config
from logging_config import get_logger

logger = get_logger(__name__)


class CommentData:
    """Data class for comment information."""

    def __init__(
        self,
        extracted_at: str,
        post_url: str,
        commenter_name: str,
        commenter_profile_url: str,
        comment_text: str,
        email: str = "",
    ):
        self.extracted_at = extracted_at
        self.post_url = post_url
        self.commenter_name = commenter_name
        self.commenter_profile_url = commenter_profile_url
        self.comment_text = comment_text
        self.email = email

    def to_dict(self) -> Dict[str, Any]:
        return {
            "extracted_at": self.extracted_at,
            "post_url": self.post_url,
            "commenter_name": self.commenter_name,
            "commenter_profile_url": self.commenter_profile_url,
            "comment_text": self.comment_text,
            "email": self.email,
        }


class LinkedInCommentExtractor:
    """Extracts comments from LinkedIn posts."""

    # CSS Selectors (legacy; current extraction uses BeautifulSoup selectors)
    COMMENT_CONTAINER_SELECTOR = "div[data-comment-id]"
    COMMENTER_NAME_SELECTOR = "button[data-control-name='comment_author_name']"
    PROFILE_URL_SELECTOR = "a[href*='/in/']"
    COMMENT_TEXT_SELECTOR = "span[dir='ltr']"

    def __init__(self, browser_manager: BrowserManager, post_url: str):
        if not URLValidator.is_valid_linkedin_post_url(post_url):
            raise ValueError(f"Invalid LinkedIn post URL: {post_url}")

        self.browser_manager = browser_manager
        self.post_url = post_url
        self.comments: List[CommentData] = []

    async def extract_comments(self) -> List[CommentData]:
        """Extract all comments from the post."""
        try:
            logger.info(f"Starting comment extraction from {self.post_url}")

            await self.browser_manager.goto(self.post_url)
            await asyncio.sleep(Config.WAIT_FOR_LOAD_TIME / 1000)

            await self._load_all_comments()
            await self._extract_comment_data()

            logger.info(f"Successfully extracted {len(self.comments)} comments")
            return self.comments

        except Exception as e:
            logger.error(f"Failed to extract comments: {str(e)}")
            return []

    async def _load_all_comments(self) -> None:
        """Load all comments by clicking load-more buttons and scrolling."""
        try:
            logger.info("Loading comments...")
            await asyncio.sleep(5)

            # Best-effort: click expansion buttons if present.
            texts_round_1 = [
                "View more comments",
                "Show more comments",
                "Load more comments",
                "View previous comments",
            ]
            for text in texts_round_1:
                for _ in range(20):
                    try:
                        button = self.browser_manager.page.locator(f"text={text}")
                        if await button.count() > 0:
                            await button.first.click()
                            logger.info(f"Clicked: {text}")
                            await asyncio.sleep(2)
                    except Exception:
                        pass

            # Scroll to trigger lazy-loading.
            for i in range(10):
                await self.browser_manager.scroll_page(1000)
                await asyncio.sleep(2)
                logger.info(f"Scroll {i + 1}/10 completed")

            # Best-effort: try again.
            texts_round_2 = [
                "View more comments",
                "Show more comments",
                "Load more comments",
                "View previous comments",
            ]
            for text in texts_round_2:
                for _ in range(20):
                    try:
                        button = self.browser_manager.page.locator(f"text={text}")
                        if await button.count() > 0:
                            await button.first.click()
                            logger.info(f"Clicked: {text}")
                            await asyncio.sleep(2)
                    except Exception:
                        pass

            # Final pass for the common button text.
            for _ in range(20):
                try:
                    button = self.browser_manager.page.locator("text=View more comments")
                    if await button.count() > 0:
                        await button.first.click()
                        logger.info("Clicked final View more comments")
                        await asyncio.sleep(2)
                except Exception:
                    pass

            logger.info("Finished scrolling")

        except Exception as e:
            logger.error(f"Error loading comments: {e}")

    async def _extract_comment_data(self) -> None:
        """Extract comments from public LinkedIn page."""
        try:
            page_content = await self.browser_manager.page.content()
            soup = BeautifulSoup(page_content, "html.parser")

            comment_sections = soup.select("section.comment")
            logger.info(f"Found {len(comment_sections)} comment sections")

            timestamp = DateTimeHelper.get_timestamp()

            for comment in comment_sections:
                try:
                    author = comment.select_one("a.comment__author")
                    commenter_name = author.get_text(strip=True) if author else "Unknown"

                    commenter_profile_url = ""
                    if author and author.get("href"):
                        commenter_profile_url = author["href"]

                    text_div = comment.select_one(".comment__text")
                    if not text_div:
                        continue

                    comment_text = DataCleaner.clean_text(
                        text_div.get_text(separator=" ", strip=True)
                    )

                    emails = EmailParser.extract_emails(comment_text)
                    email = emails[0] if emails else ""

                    self.comments.append(
                        CommentData(
                            extracted_at=timestamp,
                            post_url=self.post_url,
                            commenter_name=commenter_name,
                            commenter_profile_url=commenter_profile_url,
                            comment_text=comment_text,
                            email=email,
                        )
                    )
                except Exception as e:
                    logger.warning(f"Comment parse failed: {e}")

            logger.info(f"Extracted {len(self.comments)} comments")

        except Exception as e:
            logger.error(f"Failed extraction: {e}")

    def _parse_comment_container(
        self, container: Any, timestamp: str
    ) -> Optional[CommentData]:
        """Parse individual comment container."""
        try:
            name_element = container.find(
                "button", {"data-control-name": "comment_author_name"}
            )
            commenter_name = (
                DataCleaner.clean_text(name_element.get_text()) if name_element else "Unknown"
            )

            profile_link = container.find("a", href=lambda x: x and "/in/" in x)
            commenter_profile_url = profile_link.get("href", "") if profile_link else ""

            comment_text_elements = container.find_all("span", {"dir": "ltr"})
            comment_text = " ".join(
                [DataCleaner.clean_text(elem.get_text()) for elem in comment_text_elements]
            )

            if not comment_text:
                return None

            emails = EmailParser.extract_emails(comment_text)
            email = emails[0] if emails else ""

            return CommentData(
                extracted_at=timestamp,
                post_url=self.post_url,
                commenter_name=commenter_name,
                commenter_profile_url=commenter_profile_url,
                comment_text=comment_text,
                email=email,
            )

        except Exception as e:
            logger.error(f"Failed to parse comment container: {str(e)}")
            return None

    def remove_duplicates(self) -> int:
        """Remove duplicate comments."""
        original_count = len(self.comments)

        comment_dicts = [c.to_dict() for c in self.comments]
        unique_dicts = DataCleaner.remove_duplicates(comment_dicts, "comment_text")

        self.comments = [CommentData(**comment_dict) for comment_dict in unique_dicts]

        duplicates_removed = original_count - len(self.comments)
        logger.info(f"Removed {duplicates_removed} duplicate comments")
        return duplicates_removed

