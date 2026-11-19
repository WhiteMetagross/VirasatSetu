import os
import re
import html
from typing import Optional
from fastapi import HTTPException, status

# Allowed file extensions and MIME types for document repository
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/webp"
}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 Megabytes

# Common SQL injection patterns for signature based defense in depth
SQLI_PATTERNS = [
    r"(\b(UNION(\s+ALL)?)\b.*?\bSELECT\b)",
    r"(\bOR\b\s+['\"]?1['\"]?\s*=\s*['\"]?1)",
    r"(\bAND\b\s+['\"]?1['\"]?\s*=\s*['\"]?2)",
    r"(;\s*DROP\s+TABLE\b)",
    r"(;\s*DELETE\s+FROM\b)",
    r"(;\s*INSERT\s+INTO\b)",
    r"(;\s*UPDATE\b.*?\bSET\b)",
    r"(\bEXEC(\s+|\().*?\b)",
    r"(\bSLEEP\s*\(\s*\d+\s*\))",
    r"(--|/\*|\*/)"
]
SQLI_REGEX = re.compile("|".join(SQLI_PATTERNS), re.IGNORECASE)

# Dangerous XSS script patterns
XSS_PATTERNS = [
    r"<\s*script\b",
    r"javascript\s*:",
    r"vbscript\s*:",
    r"data\s*:\s*text\/html",
    r"on(load|error|click|mouseover|focus|blur|change|submit)\s*=",
    r"<\s*iframe\b",
    r"<\s*object\b",
    r"<\s*embed\b"
]
XSS_REGEX = re.compile("|".join(XSS_PATTERNS), re.IGNORECASE)


def sanitize_text(value: Optional[str]) -> Optional[str]:
    """
    Sanitizes user input strings by stripping dangerous control characters
    and applying HTML entity encoding to prevent stored and reflected XSS.
    """
    if value is None:
        return None
    val = value.strip()
    if not val:
        return ""
    # Strip null bytes and control characters
    val = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", val)
    # Apply HTML entity encoding
    return html.escape(val, quote=True)


def validate_input_safety(value: Optional[str], field_name: str = "Input") -> str:
    """
    Validates that user input does not contain blatant SQL injection or XSS payloads.
    Throws HTTP 400 Bad Request if a malicious payload is detected.
    """
    if not value:
        return value or ""
    
    # Check for SQL injection patterns
    if SQLI_REGEX.search(value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Security alert: Malicious SQL injection sequence detected in {field_name}."
        )
    
    # Check for XSS script injection patterns
    if XSS_REGEX.search(value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Security alert: Malicious script sequence detected in {field_name}."
        )
    
    return sanitize_text(value)


def validate_file_upload(filename: str, content: bytes, content_type: Optional[str] = None) -> str:
    """
    Validates uploaded file extension, size, and content type to prevent
    arbitrary file upload, web shell execution, and path traversal attacks.
    """
    # Prevent path traversal like ../../etc/passwd or embedded path separators
    if not filename or ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security alert: Path traversal or invalid directory separators detected."
        )

    clean_name = os.path.basename(filename).strip()
    if not clean_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security alert: Invalid file path or filename."
        )

    # Check extension
    ext = os.path.splitext(clean_name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        allowed_list = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file format '{ext}'. Allowed document formats: {allowed_list}."
        )

    # Check size limit
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds maximum permitted limit of 10 Megabytes."
        )

    # Check MIME type
    if content_type and content_type.lower() not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid MIME content type detected for document upload."
        )

    return clean_name
