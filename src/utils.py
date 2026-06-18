"""Utility functions module."""
from typing import Optional, Dict, Any, List
from datetime import datetime
import re
from urllib.parse import urljoin, urlparse
from logging_config import get_logger

logger = get_logger(__name__)


class URLValidator:
    """URL validation utilities."""

    @staticmethod
    def is_valid_linkedin_post_url(url: str) -> bool:
        """Validate if URL is a valid LinkedIn post URL."""
        linkedin_patterns = [
            r"linkedin\.com/feed/update",
            r"linkedin\.com/posts",
            r"linkedin\.com/pulse",
        ]

        for pattern in linkedin_patterns:
            if re.search(pattern, url):
                return True

        return False

    @staticmethod
    def extract_post_id(url: str) -> Optional[str]:
        """Extract post ID from LinkedIn URL."""
        try:
            # Try to extract from update URL
            match = re.search(r"update/(\d+)", url)
            if match:
                return match.group(1)

            # Try to extract from activity ID
            match = re.search(r"activity-(\d+)", url)
            if match:
                return match.group(1)

            return None
        except Exception as e:
            logger.error(f"Failed to extract post ID: {str(e)}")
            return None

    @staticmethod
    def extract_profile_url(relative_url: str, base_url: str = "https://www.linkedin.com") -> str:
        """Extract full profile URL."""
        if relative_url.startswith("http"):
            return relative_url
        return urljoin(base_url, relative_url)


class DataCleaner:
    """Data cleaning utilities."""

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""

        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)
        # Strip leading/trailing whitespace
        text = text.strip()
        return text

    @staticmethod
    def remove_duplicates(items: List[Dict[str, Any]], key: str) -> List[Dict[str, Any]]:
        """Remove duplicate items based on key."""
        seen: set = set()
        unique_items: List[Dict[str, Any]] = []

        for item in items:
            item_key = item.get(key, "")
            if item_key not in seen:
                seen.add(item_key)
                unique_items.append(item)

        logger.info(f"Removed {len(items) - len(unique_items)} duplicates")
        return unique_items

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for file system."""
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', "", filename)
        # Remove leading/trailing dots and spaces
        filename = filename.strip(". ")
        return filename


class DateTimeHelper:
    """DateTime utilities."""

    @staticmethod
    def get_timestamp() -> str:
        """Get current timestamp in ISO format."""
        return datetime.now().isoformat()

    @staticmethod
    def get_formatted_datetime() -> str:
        """Get formatted datetime string."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def get_filename_timestamp() -> str:
        """Get timestamp suitable for filenames."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")


class RetryHelper:
    """Retry mechanism utilities."""

    @staticmethod
    def calculate_backoff(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
        """Calculate exponential backoff delay."""
        delay = min(base_delay * (2 ** attempt), max_delay)
        return delay

    @staticmethod
    def should_retry(attempt: int, max_attempts: int) -> bool:
        """Check if should retry."""
        return attempt < max_attempts
