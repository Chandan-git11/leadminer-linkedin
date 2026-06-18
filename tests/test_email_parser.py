"""Unit tests for email parser module."""
import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from email_parser import EmailParser


class TestEmailParser:
    """Test cases for EmailParser."""

    def test_extract_single_email(self):
        """Test extracting single email from text."""
        text = "Contact me at john.doe@example.com for more info"
        emails = EmailParser.extract_emails(text)

        assert len(emails) == 1
        assert emails[0] == "john.doe@example.com"

    def test_extract_multiple_emails(self):
        """Test extracting multiple emails from text."""
        text = "Reach out to john@example.com or jane@test.org"
        emails = EmailParser.extract_emails(text)

        assert len(emails) == 2
        assert "john@example.com" in emails
        assert "jane@test.org" in emails

    def test_extract_no_emails(self):
        """Test when no emails present."""
        text = "This text has no email addresses"
        emails = EmailParser.extract_emails(text)

        assert len(emails) == 0

    def test_extract_emails_from_empty_string(self):
        """Test extracting emails from empty string."""
        emails = EmailParser.extract_emails("")
        assert len(emails) == 0

    def test_extract_unique_emails(self):
        """Test extracting unique emails from multiple texts."""
        texts = [
            "Contact john@example.com",
            "Also reach jane@test.org",
            "And john@example.com again",
        ]
        unique_emails = EmailParser.extract_unique_emails(texts)

        assert len(unique_emails) == 2
        assert "john@example.com" in unique_emails
        assert "jane@test.org" in unique_emails

    def test_validate_email_valid(self):
        """Test validating valid email."""
        assert EmailParser.validate_email("test@example.com") is True
        assert EmailParser.validate_email("user.name+tag@example.co.uk") is True

    def test_validate_email_invalid(self):
        """Test validating invalid email."""
        assert EmailParser.validate_email("invalid.email") is False
        assert EmailParser.validate_email("@example.com") is False
        assert EmailParser.validate_email("test@") is False

    def test_is_professional_email_true(self):
        """Test professional email detection."""
        assert EmailParser.is_professional_email("john@company.com") is True
        assert EmailParser.is_professional_email("jane@acme.org") is True

    def test_is_professional_email_false(self):
        """Test non-professional email detection."""
        assert EmailParser.is_professional_email("john@gmail.com") is False
        assert EmailParser.is_professional_email("jane@yahoo.com") is False
        assert EmailParser.is_professional_email("test@outlook.com") is False

    def test_complex_email_extraction(self):
        """Test extracting emails from complex text."""
        text = """
        Hello! You can reach me at support@mycompany.com or
        for urgent matters contact emergency@mycompany.com.
        Personal email: john.doe@gmail.com
        """
        emails = EmailParser.extract_emails(text)

        assert len(emails) == 3
        assert "support@mycompany.com" in emails
        assert "emergency@mycompany.com" in emails
        assert "john.doe@gmail.com" in emails


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
