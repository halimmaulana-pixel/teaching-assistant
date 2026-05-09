"""Group assignment creation command."""
import re
import logging

logger = logging.getLogger("teaching-assistant")

async def handle_create_group_assignment(message, bot_instance):
    """Handle !create-group-assignment command."""
    content = message.content
    if not content.startswith("!create-group-assignment"):
        return

    from teaching_assistant.commands.assignment import parse_assignment_command
    args = parse_assignment_command(content)

    required = ["title", "deadline"]
    missing = [k for k in required if k not in args]
    if missing:
        await message.reply(f"❌ Missing required fields: {', '.join(missing)}\n\nUsage:\n```!create-group-assignment title:\"...\" deadline:\"...\"```")
        return

    default_classes = ["d1-si", "c1-si", "e1-si", "g1-si", "a2-si", "h1-si", "a1-si", "b1-si", "f1-si"]
    classes = [c.strip() for c in args.get("classes", ",".join(default_classes)).split(",")]

    from teaching_assistant.services.database import create_assignment, init_db
    await init_db()

    assignment = {
        "title": args["title"],
        "description": args.get("desc", ""),
        "deadline": args["deadline"],
        "classes": classes,
        "grading_prompt": args.get("grading_prompt", ""),
        "created_by": str(message.author.id),
        "assignment_type": "group"
    }

    assignment_id = await create_assignment(**assignment)
    assignment["id"] = assignment_id

    guild = message.guild
    from teaching_assistant.services.thread_manager import create_group_assignment_threads
    results = await create_group_assignment_threads(guild, assignment)

    success = [k for k, v in results.items() if v["status"] == "created"]
    failed = [k for k, v in results.items() if v["status"] != "created"]

    response = f"✅ Group Assignment created: **{assignment['title']}**\n\n📁 Threads created in: {', '.join(success) if success else 'none'}"
    if failed:
        response += f"\n❌ Failed: {', '.join(failed)}"

    await message.reply(response)