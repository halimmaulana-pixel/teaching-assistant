"""General commands: help, list-assignments."""
import logging

logger = logging.getLogger("teaching-assistant")

HELP_TEXT = """
📚 **Teaching Assistant Bot - Help**

**Commands:**
`!create-assignment title:"..." desc:"..." deadline:"..." classes:"d1-si,c1-si"`
   → Create new assignment (Dosen only)

`!stats <class-channel>`
   → View statistics for a class
   Example: `!stats d1-si`

`!list-assignments <class-channel>`
   → List all assignments for a class

`!mygrade <assignment-id>`
   → View your grade for an assignment

`!help`
   → Show this help message

**Submission Format:**
```
NIM: [your_nim]
---
[your work: link, code, etc]
```
"""

async def handle_help(message):
    """Handle !help command."""
    await message.reply(HELP_TEXT)

async def handle_list_assignments(message, bot_instance):
    """Handle !list-assignments command."""
    content = message.content.strip()
    args = content.split()[1:] if len(content.split()) > 1 else []

    class_channel = args[0] if args else None

    from teaching_assistant.services.database import init_db, get_all_assignments
    await init_db()

    assignments = await get_all_assignments()

    if class_channel:
        assignments = [a for a in assignments if class_channel in a["classes"]]

    if not assignments:
        await message.reply("❌ No assignments found.")
        return

    text = "📚 **Assignments:**\n\n"
    for a in assignments:
        status = "🟢 Active" if a["status"] == "active" else "🔴 Closed"
        text += f"**{a['title']}** {status}\n"
        text += f"   Deadline: {a['deadline']}\n"
        text += f"   Classes: {', '.join(a['classes'])}\n\n"

    await message.reply(text)