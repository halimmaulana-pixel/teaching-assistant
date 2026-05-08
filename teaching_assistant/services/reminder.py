"""Reminder system for deadlines."""
import logging
import asyncio
from datetime import datetime, timedelta
import discord

logger = logging.getLogger("teaching-assistant")

async def check_deadlines(bot):
    """Check for upcoming deadlines and send reminders."""
    from teaching_assistant.services.database import get_all_assignments

    assignments = await get_all_assignments()

    for assignment in assignments:
        if assignment["status"] != "active":
            continue

        deadline = parse_deadline(assignment["deadline"])
        if not deadline:
            continue

        now = datetime.now()
        time_diff = deadline - now

        if timedelta(hours=23) <= time_diff <= timedelta(hours=24):
            await send_reminder(bot, assignment, "24 hours")
        elif timedelta(minutes=59) <= time_diff <= timedelta(hours=1):
            await send_reminder(bot, assignment, "1 hour")
        elif timedelta(hours=-1) <= time_diff < timedelta(0):
            await send_deadline_passed(bot, assignment)

def parse_deadline(deadline_str: str):
    """Parse deadline string to datetime."""
    formats = ["%Y-%m-%d %H:%M", "%Y-%m-%d", "%d/%m/%Y %H:%M"]
    for fmt in formats:
        try:
            return datetime.strptime(deadline_str, fmt)
        except ValueError:
            continue
    return None

async def send_reminder(bot, assignment, time_label):
    """Send deadline reminder."""
    guild = bot.client.get_guild(bot.guild_id)
    if not guild:
        return

    for class_channel_name in assignment["classes"]:
        channel = discord.utils.get(guild.text_channels, name=class_channel_name)
        if channel:
            await channel.send(f"⏰ **REMINDER: {assignment['title']}**\n📅 Deadline in {time_label}!\n⏰ {assignment['deadline']}")

async def send_deadline_passed(bot, assignment):
    """Send deadline passed notification."""
    logger.info(f"Deadline passed for: {assignment['title']}")