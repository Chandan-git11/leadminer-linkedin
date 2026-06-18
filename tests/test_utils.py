"""Unit tests for utils module."""
import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import URLValidator, DataCleaner, DateTimeHelper, RetryHelper


class TestURLValidator:
    """Test cases for URLValidator."""

    def test_valid_feed_update_url(self):
        """Test valid LinkedIn feed update URL."""
        url = "https://www.linkedin.com/feed/update/urn:li:activity:6878901234567890/"
        assert URLValidator.is_valid_linkedin_post_url(url) is True

    def test_valid_posts_url(self):
        """Test valid LinkedIn posts URL."""
        url = "https://www.linkedin.com/posts/username_activity-1234567890"
        assert URLValidator.is_valid_linkedin_post_url(url) is True

    def test_valid_pulse_url(self):
        """Test valid LinkedIn pulse URL."""
        url = "https://www.linkedin.com/pulse/title-username-abc123"
        assert URLValidator.is_valid_linkedin_post_url(url) is True

    def test_invalid_url(self):
        """Test invalid URL."""
        url = "https://www.linkedin.com/in/username"
        assert URLValidator.is_valid_linkedin_post_url(url) is False

    def test_extract_post_id_from_update(self):
        """Test extracting post ID from update URL."""
        url = "https://www.linkedin.com/feed/update/urn:li:activity:6878901234567890/"
        post_id = URLValidator.extract_post_id(url)

        assert post_id == "6878901234567890"

    def test_extract_post_id_from_activity(self):
        """Test extracting post ID from activity URL."""
        url = "https://www.linkedin.com/posts/username_activity-1234567890"
        post_id = URLValidator.extract_post_id(url)

        assert post_id == "1234567890"

    def test_extract_profile_url_absolute(self):
        """Test extracting absolute profile URL."""
        url = "https://www.linkedin.com/in/john-doe"
        result = URLValidator.extract_profile_url(url)

        assert result == url

    def test_extract_profile_url_relative(self):
        """Test extracting relative profile URL."""
        url = "/in/john-doe"
        result = URLValidator.extract_profile_url(url)

        assert result == "https://www.linkedin.com/in/john-doe"


class TestDataCleaner:
    """Test cases for DataCleaner."""

    def test_clean_text_extra_whitespace(self):
        """Test cleaning text with extra whitespace."""
        text = "Hello   world    \n\n  test"
        cleaned = DataCleaner.clean_text(text)

        assert cleaned == "Hello world test"

    def test_clean_text_with_leading_trailing_spaces(self):
        """Test cleaning text with leading/trailing spaces."""
        text = "  hello world  "
        cleaned = DataCleaner.clean_text(text)

        assert cleaned == "hello world"

    def test_clean_text_empty_string(self):
        """Test cleaning empty string."""
        cleaned = DataCleaner.clean_text("")
        assert cleaned == ""

    def test_remove_duplicates(self):
        """Test removing duplicates."""
        items = [
            {"id": 1, "name": "Alice", "comment": "Hello"},
            {"id": 2, "name": "Bob", "comment": "World"},
            {"id": 3, "name": "Alice", "comment": "Hello"},  # Duplicate
        ]

        unique = DataCleaner.remove_duplicates(items, "comment")

        assert len(unique) == 2
        assert unique[0]["comment"] == "Hello"
        assert unique[1]["comment"] == "World"

    def test_sanitize_filename(self):
        """Test sanitizing filename."""
        filename = 'My "File" <Test> Name.txt'
        sanitized = DataCleaner.sanitize_filename(filename)

        assert '"' not in sanitized
        assert '<' not in sanitized
        assert '>' not in sanitized


class TestDateTimeHelper:
    """Test cases for DateTimeHelper."""

    def test_get_timestamp_format(self):
        """Test timestamp format."""
        timestamp = DateTimeHelper.get_timestamp()

        # Should be ISO format
        assert "T" in timestamp
        assert len(timestamp) > 10

    def test_get_formatted_datetime_format(self):
        """Test formatted datetime."""
        formatted = DateTimeHelper.get_formatted_datetime()

        # Should contain date and time
        assert "-" in formatted
        assert ":" in formatted

    def test_get_filename_timestamp_format(self):
        """Test filename timestamp format."""
        filename_ts = DateTimeHelper.get_filename_timestamp()

        # Should be suitable for filename
        assert len(filename_ts) == 15  # YYYYMMDDHHmmss
        assert "_" in filename_ts


class TestRetryHelper:
    """Test cases for RetryHelper."""

    def test_calculate_backoff_first_attempt(self):
        """Test backoff calculation for first attempt."""
        delay = RetryHelper.calculate_backoff(0, base_delay=1.0)

        assert delay == 1.0

    def test_calculate_backoff_second_attempt(self):
        """Test backoff calculation for second attempt."""
        delay = RetryHelper.calculate_backoff(1, base_delay=1.0)

        assert delay == 2.0

    def test_calculate_backoff_max_delay(self):
        """Test backoff calculation respects max delay."""
        delay = RetryHelper.calculate_backoff(
            attempt=10, base_delay=1.0, max_delay=30.0
        )

        assert delay <= 30.0

    def test_should_retry_true(self):
        """Test should retry returns true."""
        assert RetryHelper.should_retry(attempt=0, max_attempts=3) is True
        assert RetryHelper.should_retry(attempt=2, max_attempts=3) is True

    def test_should_retry_false(self):
        """Test should retry returns false."""
        assert RetryHelper.should_retry(attempt=3, max_attempts=3) is False
        assert RetryHelper.should_retry(attempt=5, max_attempts=3) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
