"""Assignment creation commands."""
import re
import logging
from discord import Embed

logger = logging.getLogger("teaching-assistant")

def parse_assignment_command(content: str) -> dict:
    """Parse !create-assignment command arguments."""
    pattern = r'(\w+):"([^"]*)"|(\w+):([^\s]+)'
    matches = re.findall(pattern, content)

    result = {}
    for m in matches:
        key = m[0] or m[2]
        value = m[1] or m[3]
        result[key] = value

    return result

async def handle_create_assignment(message, bot_instance):
    """Handle !create-assignment command."""
    content = message.content
    if not content.startswith("!create-assignment"):
        return

    args = parse_assignment_command(content)

    required = ["title", "deadline", "classes"]
    missing = [k for k in required if k not in args]
    if missing:
        await message.reply(f"❌ Missing required fields: {', '.join(missing)}\n\nUsage:\n```!create-assignment title:\"...\" deadline:\"...\" classes:\"d1-si,c1-si\"```")
        return

    classes = [c.strip() for c in args["classes"].split(",")]

    from teaching_assistant.services.database import create_assignment, init_db
    await init_db()

    assignment = {
        "title": args["title"],
        "description": args.get("desc", ""),
        "deadline": args["deadline"],
        "classes": classes,
        "grading_prompt": args.get("grading_prompt", ""),
        "created_by": str(message.author.id)
    }

    assignment_id = await create_assignment(**assignment)
    assignment["id"] = assignment_id

    guild = message.guild
    from teaching_assistant.services.thread_manager import create_assignment_threads
    results = await create_assignment_threads(guild, assignment)

    success = [k for k, v in results.items() if v["status"] == "created"]
    failed = [k for k, v in results.items() if v["status"] != "created"]

    response = f"✅ Assignment created: **{assignment['title']}**\n\n📁 Threads created in: {', '.join(success) if success else 'none'}"
    if failed:
        response += f"\n❌ Failed: {', '.join(failed)}"

    await message.reply(response)