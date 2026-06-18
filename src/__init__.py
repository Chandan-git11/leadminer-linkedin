"""LinkedIn Comment Lead Extractor package."""

__version__ = "1.0.0"
__author__ = "LinkedIn Automation Engineer"
__description__ = "Production-ready LinkedIn comment lead extractor using Playwright"

from src.config import Config
from src.browser import BrowserManager
from src.authenticator import LinkedInAuthenticator
from src.extractor import LinkedInCommentExtractor, CommentData
from src.email_parser import EmailParser
from src.exporters import ExportManager, CSVExporter, ExcelExporter, GoogleSheetsExporter

__all__ = [
    "Config",
    "BrowserManager",
    "LinkedInAuthenticator",
    "LinkedInCommentExtractor",
    "CommentData",
    "EmailParser",
    "ExportManager",
    "CSVExporter",
    "ExcelExporter",
    "GoogleSheetsExporter",
]
