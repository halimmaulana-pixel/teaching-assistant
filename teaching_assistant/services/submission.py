"""Submission detection and validation."""
import re
import logging
from typing import Optional, Tuple, List

logger = logging.getLogger("teaching-assistant")

VALID_EXTENSIONS = {
    "code": [".py", ".js", ".php", ".html", ".css", ".java", ".cpp", ".c", ".rb", ".go", ".ts"],
    "docs": [".pdf", ".txt", ".md"],
    "images": [".png", ".jpg", ".jpeg", ".gif", ".webp"],
    "archives": [".zip"]
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def extract_nim(content: str) -> Optional[str]:
    """Extract NIM from submission content."""
    match = re.search(r"^NIM:\s*(\S+)", content, re.MULTILINE)
    return match.group(1) if match else None

def extract_content_after_nim(content: str) -> str:
    """Get content after NIM line."""
    parts = content.split("---", 1)
    return parts[1].strip() if len(parts) > 1 else content

def validate_submission_format(content: str) -> Tuple[bool, Optional[str]]:
    """Validate submission format. Returns (is_valid, error_message)."""
    if not content or not content.strip():
        return False, "Konten kosong"

    nim = extract_nim(content)
    if not nim:
        return False, "❌ Format salah! Gunakan format:\n```\nNIM: [nim]\n---\n[content]\n```"

    if len(nim) < 4 or len(nim) > 20:
        return False, "❌ NIM tidak valid (harus 4-20 karakter)"

    return True, None

def validate_attachments(attachments: List[dict]) -> Tuple[bool, Optional[str]]:
    """Validate attachment file types and sizes."""
    if not attachments:
        return True, None

    all_exts = [ext for exts in VALID_EXTENSIONS.values() for ext in exts]

    for att in attachments:
        filename = att.get("filename", "")
        size = att.get("size", 0)

        ext = "." + filename.split(".")[-1].lower() if "." in filename else ""

        if ext not in all_exts:
            allowed = ", ".join(all_exts)
            return False, f"❌ File type tidak diizinkan: {ext}\nAllowed: {allowed}"

        if size > MAX_FILE_SIZE:
            return False, f"❌ File terlalu besar: {filename} (max 10MB)"

    return True, None

def parse_submission(message) -> dict:
    """Parse a Discord message into submission data."""
    return {
        "nim": extract_nim(message.content),
        "content": extract_content_after_nim(message.content),
        "attachments": [
            {
                "filename": att.filename,
                "url": att.url,
                "content_type": att.content_type,
                "size": att.size
            }
            for att in message.attachments
        ]
    }