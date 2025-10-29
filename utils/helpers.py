import os
import re
import threading
import time
from collections import deque
from pathlib import Path

from flask import current_app

_RATE_LIMIT_STATE: dict[str, deque] = {}
_RATE_LIMIT_LOCK = threading.Lock()


def clean_text(value: str | None, max_length: int) -> str:
    """Strip control characters and enforce length limits."""
    if not isinstance(value, str):
        return ""
    sanitized = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", value).strip()
    return sanitized[:max_length]


def validate_language(language: str | None) -> str | None:
    if not language:
        return None
    sanitized = clean_text(language, 32).lower()
    if not sanitized:
        return None
    allowed = current_app.config.get("ALLOWED_LANGUAGES") or []
    if allowed and sanitized not in allowed:
        raise ValueError(f"Language '{sanitized}' is not permitted")
    return sanitized


def validate_pdf_path(pdf_path: str | None) -> str | None:
    if not pdf_path:
        return None
    if not isinstance(pdf_path, str):
        raise ValueError("Invalid PDF path type")

    candidate = pdf_path.strip()
    if not candidate:
        return None

    allowed_dir = Path(current_app.config.get("ALLOWED_PDF_DIRECTORY", "")).expanduser().resolve()
    if not allowed_dir.exists():
        raise FileNotFoundError("Configured PDF directory does not exist")

    resolved = (allowed_dir / candidate).resolve()
    if not str(resolved).startswith(str(allowed_dir)):
        raise ValueError("PDF path is outside the allowed directory")

    if not resolved.is_file():
        raise FileNotFoundError("PDF file not found")

    max_bytes = current_app.config.get("MAX_PDF_SIZE_MB", 5) * 1024 * 1024
    if resolved.stat().st_size > max_bytes:
        raise ValueError("PDF exceeds allowed size")

    return str(resolved)


def enforce_rate_limit(identifier: str) -> bool:
    limit = current_app.config.get("RATE_LIMIT_REQUESTS", 60)
    window = current_app.config.get("RATE_LIMIT_WINDOW", 60)
    now = time.time()

    with _RATE_LIMIT_LOCK:
        history = _RATE_LIMIT_STATE.setdefault(identifier, deque())
        while history and now - history[0] > window:
            history.popleft()
        if len(history) >= limit:
            return False
        history.append(now)
        return True


def sanitize_output(text: str | None, max_length: int = 2048) -> str:
    if text is None:
        return ""
    sanitized = text.replace("\r", "")
    sanitized = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", sanitized)
    return sanitized[:max_length].strip()
