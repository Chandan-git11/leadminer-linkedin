"""Unit tests for extractors module."""
import pytest
from pathlib import Path
import sys
from unittest.mock import MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from exporters import CSVExporter, ExcelExporter, ExportManager


class TestCSVExporter:
    """Test cases for CSVExporter."""

    def test_export_empty_data(self):
        """Test exporting empty data."""
        exporter = CSVExporter([])
        result = exporter.export()

        # Should still succeed but with empty data
        assert result is True

    def test_export_sample_data(self):
        """Test exporting sample data."""
        data = [
            {
                "extracted_at": "2024-01-01T12:00:00",
                "post_url": "https://linkedin.com/posts/123",
                "commenter_name": "John Doe",
                "commenter_profile_url": "https://linkedin.com/in/johndoe",
                "comment_text": "Great post!",
                "email": "john@example.com",
            }
        ]

        exporter = CSVExporter(data)
        result = exporter.export()

        assert result is True


class TestExcelExporter:
    """Test cases for ExcelExporter."""

    def test_export_empty_data(self):
        """Test exporting empty data to Excel."""
        exporter = ExcelExporter([])
        result = exporter.export()

        # Should still succeed but with empty data
        assert result is True

    def test_export_sample_data(self):
        """Test exporting sample data to Excel."""
        data = [
            {
                "extracted_at": "2024-01-01T12:00:00",
                "post_url": "https://linkedin.com/posts/123",
                "commenter_name": "John Doe",
                "commenter_profile_url": "https://linkedin.com/in/johndoe",
                "comment_text": "Great post!",
                "email": "john@example.com",
            }
        ]

        exporter = ExcelExporter(data)
        result = exporter.export()

        assert result is True


class TestExportManager:
    """Test cases for ExportManager."""

    def test_export_to_csv_format(self):
        """Test exporting to CSV format."""
        data = [
            {
                "extracted_at": "2024-01-01T12:00:00",
                "post_url": "https://linkedin.com/posts/123",
                "commenter_name": "John Doe",
                "commenter_profile_url": "https://linkedin.com/in/johndoe",
                "comment_text": "Great post!",
                "email": "john@example.com",
            }
        ]

        manager = ExportManager(data)
        result = manager.export_to_format("csv")

        assert result is True

    def test_export_to_excel_format(self):
        """Test exporting to Excel format."""
        data = [
            {
                "extracted_at": "2024-01-01T12:00:00",
                "post_url": "https://linkedin.com/posts/123",
                "commenter_name": "Jane Smith",
                "commenter_profile_url": "https://linkedin.com/in/janesmith",
                "comment_text": "Interesting insights!",
                "email": "jane@example.com",
            }
        ]

        manager = ExportManager(data)
        result = manager.export_to_format("excel")

        assert result is True

    def test_export_to_invalid_format(self):
        """Test exporting to invalid format."""
        data = [{"comment_text": "Test"}]

        manager = ExportManager(data)
        result = manager.export_to_format("pdf")

        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
