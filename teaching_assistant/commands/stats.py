"""Stats command for viewing class statistics."""
import logging

logger = logging.getLogger("teaching-assistant")

async def handle_stats(message, bot_instance):
    """Handle !stats command."""
    content = message.content.strip()

    args = content.split()[1:] if len(content.split()) > 1 else []
    if not args:
        await message.reply("❌ Usage: `!stats <class-channel>`\nExample: `!stats d1-si`")
        return

    class_channel = args[0]

    from teaching_assistant.services.database import init_db, get_all_assignments, get_submissions_by_assignment

    await init_db()

    assignments = await get_all_assignments()
    if not assignments:
        await message.reply("❌ No assignments found.")
        return

    stats_text = f"📊 **Statistics for {class_channel.upper()}**\n\n"

    for assignment in assignments:
        if class_channel not in assignment["classes"]:
            continue

        submissions = await get_submissions_by_assignment(assignment["id"], class_channel)

        total = len(submissions)
        graded = sum(1 for s in submissions if s.get("score"))
        avg_score = sum(s.get("score", 0) for s in submissions if s.get("score")) / graded if graded > 0 else 0

        stats_text += f"📚 **{assignment['title']}**\n"
        stats_text += f"   ⏰ Deadline: {assignment['deadline']}\n"
        stats_text += f"   ✅ Submitted: {total}\n"
        stats_text += f"   📊 Avg Score: {avg_score:.1f}\n\n"

    await message.reply(stats_text)