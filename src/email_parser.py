"""Email parsing module using regex."""
import re
from typing import List, Set
from logging_config import get_logger

logger = get_logger(__name__)


class EmailParser:
    """Extracts email addresses from text using regex."""

    # Email regex pattern (RFC 5322 simplified)
    EMAIL_PATTERN = re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    )

    @classmethod
    def extract_emails(cls, text: str) -> List[str]:
        """Extract email addresses from text."""
        if not text:
            return []

        try:
            emails = cls.EMAIL_PATTERN.findall(text)
            return emails
        except Exception as e:
            logger.error(f"Failed to extract emails: {str(e)}")
            return []

    @classmethod
    def extract_unique_emails(cls, texts: List[str]) -> Set[str]:
        """Extract unique emails from multiple texts."""
        unique_emails: Set[str] = set()

        for text in texts:
            emails = cls.extract_emails(text)
            unique_emails.update(emails)

        return unique_emails

    @classmethod
    def validate_email(cls, email: str) -> bool:
        """Validate email format."""
        if not email:
            return False

        match = cls.EMAIL_PATTERN.match(email)
        return bool(match)

    @classmethod
    def is_professional_email(cls, email: str) -> bool:
        """Check if email is professional (not personal domains)."""
        personal_domains = {
            "gmail.com",
            "yahoo.com",
            "hotmail.com",
            "outlook.com",
            "aol.com",
        }

        try:
            domain = email.split("@")[1].lower()
            return domain not in personal_domains
        except Exception:
            return False
