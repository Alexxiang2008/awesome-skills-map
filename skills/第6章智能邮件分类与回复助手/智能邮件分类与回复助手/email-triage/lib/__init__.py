"""
Email Triage Skill - 智能邮件分类与回复助手
"""

from .email_client import (
    EmailClient,
    EmailConfig,
    EmailMessage,
    EMAIL_PROVIDERS,
    get_supported_providers,
    test_connection,
)

from .email_parser import (
    EmailFileParser,
    detect_file_type,
    parse_email_file,
)

from .processor import (
    EmailProcessor,
    ClassificationResult,
    ReplyResult,
    TodoResult,
    ProcessedEmail,
)

from .report import (
    ReportGenerator,
)

__all__ = [
    # Client
    "EmailClient",
    "EmailConfig",
    "EmailMessage",
    "EMAIL_PROVIDERS",
    "get_supported_providers",
    "test_connection",
    # Parser
    "EmailFileParser",
    "detect_file_type",
    "parse_email_file",
    # Processor
    "EmailProcessor",
    "ClassificationResult",
    "ReplyResult",
    "TodoResult",
    "ProcessedEmail",
    # Report
    "ReportGenerator",
]
