"""
Input sanitization utilities to prevent prompt injection and XSS attacks.
"""

import re
from typing import Optional
import structlog

logger = structlog.get_logger()

# Maximum length for child name after sanitization
MAX_CHILD_NAME_LENGTH = 30

# Characters allowed in child names (letters, spaces, hyphens, apostrophes)
ALLOWED_NAME_PATTERN = re.compile(r"[^a-zA-Z\s\-\']")


def sanitize_child_name(name: str) -> str:
    """
    Sanitize child name to prevent prompt injection attacks.

    Removes any characters that could be used for:
    - AI prompt injection (special chars, instructions)
    - XSS attacks in PDF/HTML output
    - SQL injection (though we use parameterized queries)

    Args:
        name: Raw child name input

    Returns:
        Sanitized name containing only letters, spaces, hyphens, and apostrophes
    """
    if not name:
        return "Child"

    # Remove any characters not in allowed set
    sanitized = ALLOWED_NAME_PATTERN.sub('', name)

    # Collapse multiple spaces into one
    sanitized = re.sub(r'\s+', ' ', sanitized)

    # Trim whitespace and limit length
    sanitized = sanitized.strip()[:MAX_CHILD_NAME_LENGTH]

    # If everything was removed, use default
    if not sanitized:
        logger.warning(
            "Child name completely sanitized to default",
            original_name=name[:50],  # Log truncated for safety
            sanitized_name="Child"
        )
        return "Child"

    # Log if significant changes were made
    if sanitized != name.strip():
        logger.info(
            "Child name sanitized",
            original_length=len(name),
            sanitized_length=len(sanitized),
            had_special_chars=bool(ALLOWED_NAME_PATTERN.search(name))
        )

    return sanitized


def sanitize_for_prompt(text: str, child_name: str) -> str:
    """
    Safely insert child name into a prompt template.

    Args:
        text: Prompt template containing {name} placeholder
        child_name: Raw child name (will be sanitized)

    Returns:
        Prompt with sanitized name inserted
    """
    safe_name = sanitize_child_name(child_name)
    return text.replace('{name}', safe_name)


def escape_for_pdf(text: str) -> str:
    """
    Escape special characters for safe PDF rendering.

    Args:
        text: Raw text to escape

    Returns:
        Escaped text safe for PDF
    """
    # Replace characters that could cause issues in PDF rendering
    escapes = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;',
    }

    for char, escape in escapes.items():
        text = text.replace(char, escape)

    return text
