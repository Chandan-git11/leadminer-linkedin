"""Export functionality module."""
from typing import List, Dict, Any, Optional
from pathlib import Path
import csv
import pandas as pd
from datetime import datetime

from utils import DataCleaner, DateTimeHelper
from config import Config
from logging_config import get_logger

logger = get_logger(__name__)


class BaseExporter:
    """Base exporter class."""

    def __init__(self, data: List[Dict[str, Any]]):
        """Initialize exporter."""
        self.data = data
        self.timestamp = DateTimeHelper.get_filename_timestamp()

    def export(self) -> bool:
        """Export data. Must be implemented by subclass."""
        raise NotImplementedError


class CSVExporter(BaseExporter):
    """Exports data to CSV file."""

    def export(self, filename: Optional[str] = None) -> bool:
        """Export data to CSV."""
        try:
            filename = filename or f"linkedin_comments_{self.timestamp}.csv"
            filepath = Path(Config.OUTPUT_DIR) / filename

            df = pd.DataFrame(self.data)
            df.to_csv(filepath, index=False, encoding="utf-8")

            logger.info(f"Exported {len(self.data)} records to CSV: {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to export to CSV: {str(e)}")
            return False


class ExcelExporter(BaseExporter):
    """Exports data to Excel file."""

    def export(self, filename: Optional[str] = None) -> bool:
        """Export data to Excel."""
        try:
            filename = filename or f"linkedin_comments_{self.timestamp}.xlsx"
            filepath = Path(Config.OUTPUT_DIR) / filename

            df = pd.DataFrame(self.data)

            with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Comments")

                # Auto-adjust column widths
                worksheet = writer.sheets["Comments"]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter

                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(cell.value)
                        except Exception:
                            pass

                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width

            logger.info(f"Exported {len(self.data)} records to Excel: {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to export to Excel: {str(e)}")
            return False


class GoogleSheetsExporter(BaseExporter):
    """Exports data to Google Sheets."""

    def __init__(self, data: List[Dict[str, Any]]):
        """Initialize Google Sheets exporter."""
        super().__init__(data)

        try:
            import gspread
            from google.oauth2.service_account import Credentials

            self.gspread = gspread
            self.Credentials = Credentials
        except ImportError:
            logger.error(
                "gspread or google-auth not installed. Install with: pip install gspread google-auth-oauthlib"
            )
            raise

    def export(self, spreadsheet_id: Optional[str] = None) -> bool:
        """Export data to Google Sheets."""
        try:
            spreadsheet_id = spreadsheet_id or Config.GOOGLE_SHEETS_SPREADSHEET_ID
            credentials_file = Config.GOOGLE_SHEETS_CREDENTIALS

            if not spreadsheet_id:
                logger.error("Spreadsheet ID not provided")
                return False

            if not credentials_file or not Path(credentials_file).exists():
                logger.error(f"Credentials file not found: {credentials_file}")
                return False

            # Authenticate
            credentials = self.Credentials.from_service_account_file(
                credentials_file,
                scopes=["https://www.googleapis.com/auth/spreadsheets"],
            )

            client = self.gspread.authorize(credentials)
            sheet = client.open_by_key(spreadsheet_id)

            # Use first worksheet or create new one
            worksheet = sheet.sheet1

            # Clear existing data
            worksheet.clear()

            # Add header
            if self.data:
                headers = list(self.data[0].keys())
                worksheet.append_row(headers)

                # Add data rows
                for record in self.data:
                    row = [record.get(key, "") for key in headers]
                    worksheet.append_row(row)

            logger.info(f"Exported {len(self.data)} records to Google Sheets")
            return True

        except Exception as e:
            logger.error(f"Failed to export to Google Sheets: {str(e)}")
            return False


class ExportManager:
    """Manages data exports to multiple formats."""

    def __init__(self, data: List[Dict[str, Any]]):
        """Initialize export manager."""
        self.data = data
        Config.ensure_output_dir()

    def export_all(self) -> Dict[str, bool]:
        """Export to all configured formats."""
        results = {}

        try:
            if Config.EXPORT_TO_CSV:
                csv_exporter = CSVExporter(self.data)
                results["csv"] = csv_exporter.export()

            if Config.EXPORT_TO_EXCEL:
                excel_exporter = ExcelExporter(self.data)
                results["excel"] = excel_exporter.export()

            if Config.EXPORT_TO_GSHEETS:
                try:
                    gsheets_exporter = GoogleSheetsExporter(self.data)
                    results["gsheets"] = gsheets_exporter.export()
                except ImportError:
                    logger.warning(
                        "Skipping Google Sheets export - required packages not installed"
                    )
                    results["gsheets"] = False

        except Exception as e:
            logger.error(f"Export failed: {str(e)}")
            return results

        logger.info(f"Export results: {results}")
        return results

    def export_to_format(self, format_type: str) -> bool:
        """Export to specific format."""
        format_type = format_type.lower()

        if format_type == "csv":
            exporter = CSVExporter(self.data)
            return exporter.export()

        elif format_type == "excel":
            exporter = ExcelExporter(self.data)
            return exporter.export()

        elif format_type == "gsheets":
            try:
                exporter = GoogleSheetsExporter(self.data)
                return exporter.export()
            except ImportError:
                logger.error("Google Sheets export not available")
                return False

        else:
            logger.error(f"Unknown export format: {format_type}")
            return False
