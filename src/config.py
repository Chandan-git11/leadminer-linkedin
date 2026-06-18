"""Configuration management module."""
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


class Config:
    """Configuration class for the LinkedIn extractor."""

    # LinkedIn Credentials
    LINKEDIN_EMAIL: str = os.getenv("LINKEDIN_EMAIL", "")
    LINKEDIN_PASSWORD: str = os.getenv("LINKEDIN_PASSWORD", "")

    # Browser Settings
    HEADLESS_MODE: bool = os.getenv("HEADLESS_MODE", "True").lower() == "true"
    BROWSER_TIMEOUT: int = int(os.getenv("BROWSER_TIMEOUT", "30000"))
    WAIT_FOR_LOAD_TIME: int = int(os.getenv("WAIT_FOR_LOAD_TIME", "5000"))

    # Extraction Settings
    MAX_SCROLLS: int = int(os.getenv("MAX_SCROLLS", "10"))
    SCROLL_DELAY: float = float(os.getenv("SCROLL_DELAY", "1.5"))
    COMMENT_LOAD_RETRY: int = int(os.getenv("COMMENT_LOAD_RETRY", "3"))

    # Session Management
    SESSION_STORAGE_PATH: str = os.getenv(
        "SESSION_STORAGE_PATH", "./config/sessions"
    )
    USE_SAVED_COOKIES: bool = os.getenv("USE_SAVED_COOKIES", "True").lower() == "true"

    # Google Sheets
    GOOGLE_SHEETS_CREDENTIALS: str = os.getenv("GOOGLE_SHEETS_CREDENTIALS", "")
    GOOGLE_SHEETS_SPREADSHEET_ID: str = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID", "")

    # Output Settings
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "./output")
    EXPORT_TO_EXCEL: bool = os.getenv("EXPORT_TO_EXCEL", "True").lower() == "true"
    EXPORT_TO_CSV: bool = os.getenv("EXPORT_TO_CSV", "True").lower() == "true"
    EXPORT_TO_GSHEETS: bool = os.getenv("EXPORT_TO_GSHEETS", "False").lower() == "true"

    # Logging Settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR: str = os.getenv("LOG_DIR", "./logs")

    @classmethod
    def validate(cls) -> bool:
        """Validate critical configuration values."""
        required_fields = ["LINKEDIN_EMAIL", "LINKEDIN_PASSWORD"]
        for field in required_fields:
            if not getattr(cls, field):
                return False
        return True

    @classmethod
    def get_session_file(cls, username: Optional[str] = None) -> Path:
        """Get path to session storage file."""
        session_dir = Path(cls.SESSION_STORAGE_PATH)
        session_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{username}_session.json" if username else "default_session.json"
        return session_dir / filename

    @classmethod
    def ensure_output_dir(cls) -> Path:
        """Ensure output directory exists."""
        output_path = Path(cls.OUTPUT_DIR)
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path

    @classmethod
    def ensure_log_dir(cls) -> Path:
        """Ensure log directory exists."""
        log_path = Path(cls.LOG_DIR)
        log_path.mkdir(parents=True, exist_ok=True)
        return log_path
