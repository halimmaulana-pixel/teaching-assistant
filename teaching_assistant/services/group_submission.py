"""Group submission detection and validation."""
import re
import logging
from typing import Optional, Tuple, List

logger = logging.getLogger("teaching-assistant")

def parse_group_submission(content: str) -> dict:
    """Parse a group submission from message content.

    Expected format:
    Nama Tim: [nama_tim]
    Link Repo: [url]
    Link Deploy: [url]
    Job Desc: [description]
    ---
    NIM: [nim] - Job Desc: [role]
    NIM: [nim] - Job Desc: [role]
    ...
    """
    lines = content.strip().split('\n')
    result = {
        "team_name": None,
        "repo_url": None,
        "deploy_url": None,
        "project_description": None,
        "members": []
    }

    section = "header"
    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line == "---":
            section = "members"
            continue

        if section == "header":
            if line.startswith("Nama Tim:"):
                result["team_name"] = line.split(":", 1)[1].strip()
            elif line.startswith("Link Repo:"):
                result["repo_url"] = line.split(":", 1)[1].strip()
            elif line.startswith("Link Deploy:"):
                result["deploy_url"] = line.split(":", 1)[1].strip()
            elif line.startswith("Job Desc:"):
                result["project_description"] = line.split(":", 1)[1].strip()

        elif section == "members":
            match = re.match(r"NIM:\s*(\S+)\s*-\s*Job Desc:\s*(.+)", line, re.IGNORECASE)
            if match:
                result["members"].append({
                    "nim": match.group(1),
                    "role": match.group(2).strip()
                })

    return result

def validate_group_submission_format(content: str) -> Tuple[bool, Optional[str]]:
    """Validate group submission format. Returns (is_valid, error_message)."""
    if not content or not content.strip():
        return False, "Konten kosong"

    data = parse_group_submission(content)

    errors = []

    if not data["team_name"]:
        errors.append("Nama Tim wajib diisi")

    if not data["repo_url"]:
        errors.append("Link Repo wajib diisi")

    if not data["deploy_url"]:
        errors.append("Link Deploy wajib diisi")

    if not data["project_description"]:
        errors.append("Job Desc wajib diisi")

    if len(data["members"]) < 5:
        errors.append(f"Minimal 5 anggota (1 Ketua + 4 Anggota). Ditemukan: {len(data['members'])}")

    if errors:
        return False, "❌ Format salah!\n" + "\n".join([f"  • {e}" for e in errors])

    return True, None