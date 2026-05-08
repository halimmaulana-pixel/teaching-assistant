"""Discord bot client for Teaching Assistant."""
import logging
import os
from typing import Optional
import discord
from discord import Intents

logger = logging.getLogger("teaching-assistant")

class Bot:
    """Main Discord bot class."""

    def __init__(self):
        self.client: Optional[discord.Client] = None
        self.guild_id: Optional[int] = None
        self.db_path: Optional[str] = None
        self._load_config()

    def _load_config(self) -> dict:
        """Load configuration from environment variables."""
        self.guild_id = int(os.getenv("DISCORD_GUILD_ID", "0"))
        self.db_path = os.getenv("DATABASE_PATH", "./data/teaching_assistant.db")
        return {
            "TOKEN": os.getenv("DISCORD_TOKEN"),
        }

    async def run(self):
        """Run the bot."""
        intents = Intents.default()
        intents.message_content = True
        intents.guilds = True

        self.client = discord.Client(intents=intents)

        @self.client.event
        async def on_ready():
            logger.info(f"Bot connected: {self.client.user.name}#{self.client.user.discriminator}")
            logger.info(f"Guild ID: {self.guild_id}")

        @self.client.event
        async def on_message(message: discord.Message):
            await self.handle_message(message)

        token = self._load_config()["TOKEN"]
        if not token:
            raise ValueError("DISCORD_TOKEN environment variable is required.")

        await self.client.start(token)

    async def handle_message(self, message: discord.Message):
        """Handle incoming messages."""
        if message.author.bot:
            return

        if isinstance(message.channel, discord.Thread):
            thread_name = message.channel.name
            if thread_name.startswith("tugas-"):
                await self.handle_submission(message, message.channel)
                return

        content = message.content.strip()

        if content.startswith("!create-assignment"):
            from teaching_assistant.commands.assignment import handle_create_assignment
            await handle_create_assignment(message, self)
        elif content.startswith("!stats"):
            from teaching_assistant.commands.stats import handle_stats
            await handle_stats(message, self)
        elif content.startswith("!help"):
            from teaching_assistant.commands.general import handle_help
            await handle_help(message)
        elif content.startswith("!list-assignments"):
            from teaching_assistant.commands.general import handle_list_assignments
            await handle_list_assignments(message, self)

    async def handle_submission(self, message: discord.Message, thread: discord.Thread):
        """Handle assignment submission in thread."""
        from teaching_assistant.services.submission import validate_submission_format, validate_attachments, parse_submission
        from teaching_assistant.services.database import init_db, get_assignment_by_thread_slug, check_submission_exists, create_submission

        await init_db()

        is_valid, error = validate_submission_format(message.content)
        if not is_valid:
            await thread.send(error)
            return

        submission_data = parse_submission(message)
        nim = submission_data["nim"]

        is_valid, error = validate_attachments(submission_data["attachments"])
        if not is_valid:
            await thread.send(error)
            return

        assignment = await get_assignment_by_thread_slug(thread.name)
        if not assignment:
            logger.warning(f"No assignment found for thread: {thread.name}")
            return

        exists = await check_submission_exists(assignment["id"], nim)
        if exists:
            await thread.send("⚠️ Kamu sudah submit tugas ini. Hanya 1 submission yang diterima.")
            return

        submission_id = await create_submission(
            assignment_id=assignment["id"],
            nim=nim,
            student_name=message.author.name,
            student_discord_id=str(message.author.id),
            class_channel=message.channel.parent.name,
            content=submission_data["content"],
            attachments=submission_data["attachments"]
        )

        await thread.send(f"✅ Submission received!\n📋 NIM: {nim}\n⏰ Time: {discord.utils.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n🔍 AI grading in progress...")
        logger.info(f"New submission: {nim} for assignment {assignment['title']}")