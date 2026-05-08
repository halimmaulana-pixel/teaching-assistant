"""Grading service - formats grade output for Discord."""
import logging

logger = logging.getLogger("teaching-assistant")

def format_grade_embed(submission: dict, assignment_title: str) -> dict:
    """Format grade result as Discord embed."""
    score = submission.get("score", 0)
    feedback = submission.get("feedback", "")
    strengths = submission.get("strengths", [])
    improvements = submission.get("improvements", [])
    nim = submission.get("nim", "Unknown")

    if score >= 80:
        color = 0x00FF00
    elif score >= 60:
        color = 0xFFFF00
    else:
        color = 0xFF0000

    embed = {
        "title": f"📊 Grade Result - {assignment_title}",
        "color": color,
        "fields": [
            {"name": "NIM", "value": nim, "inline": True},
            {"name": "Score", "value": f"{score}/100", "inline": True},
        ]
    }

    if strengths:
        strength_text = "\n".join([f"✅ {s}" for s in strengths])
        embed["fields"].append({"name": "Strengths", "value": strength_text, "inline": False})

    if feedback:
        embed["fields"].append({"name": "Feedback", "value": feedback, "inline": False})

    if improvements:
        improve_text = "\n".join([f"💡 {i}" for i in improvements])
        embed["fields"].append({"name": "Improvements", "value": improve_text, "inline": False})

    return embed