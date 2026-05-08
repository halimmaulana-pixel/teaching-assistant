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
        elif content.startswith("!create-group-assignment"):
            from teaching_assistant.commands.group_assignment import handle_create_group_assignment
            await handle_create_group_assignment(message, self)
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
        from teaching_assistant.services.database import init_db, get_assignment_by_thread_slug

        await init_db()

        assignment = await get_assignment_by_thread_slug(thread.name)
        if not assignment:
            logger.warning(f"No assignment found for thread: {thread.name}")
            return

        if assignment.get("assignment_type") == "group":
            await self.handle_group_submission(message, thread, assignment)
        else:
            await self.handle_individual_submission(message, thread, assignment)

    async def handle_individual_submission(self, message: discord.Message, thread: discord.Thread, assignment: dict):
        """Handle individual assignment submission."""
        from teaching_assistant.services.submission import validate_submission_format, validate_attachments, parse_submission
        from teaching_assistant.services.database import check_submission_exists, create_submission

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
        logger.info(f"New individual submission: {nim} for assignment {assignment['title']}")

    async def handle_group_submission(self, message: discord.Message, thread: discord.Thread, assignment: dict):
        """Handle group assignment submission."""
        from teaching_assistant.services.group_submission import validate_group_submission_format, parse_group_submission
        from teaching_assistant.services.database import check_group_submission_exists, create_group_submission

        is_valid, error = validate_group_submission_format(message.content)
        if not is_valid:
            await thread.send(error)
            return

        submission_data = parse_group_submission(message)

        exists = await check_group_submission_exists(assignment["id"], submission_data["team_name"])
        if exists:
            await thread.send("⚠️ Tim ini sudah submit tugas ini. Hanya 1 submission yang diterima.")
            return

        submission_id = await create_group_submission(
            assignment_id=assignment["id"],
            team_name=submission_data["team_name"],
            repo_url=submission_data["repo_url"],
            deploy_url=submission_data["deploy_url"],
            project_description=submission_data["project_description"],
            submitted_by_discord_id=str(message.author.id),
            submitted_by_name=message.author.name,
            class_channel=message.channel.parent.name,
            members=submission_data["members"]
        )

        members_info = "\n".join([f"• {m['nim']} - {m['role']}" for m in submission_data["members"]])
        await thread.send(
            f"✅ Group Submission received!\n"
            f"📋 Nama Tim: {submission_data['team_name']}\n"
            f"🔗 Repo: {submission_data['repo_url']}\n"
            f"🔗 Deploy: {submission_data['deploy_url']}\n"
            f"⏰ Time: {discord.utils.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"👥 Anggota:\n{members_info}\n\n"
            f"🔍 AI grading in progress..."
        )

        grading_channel = discord.utils.get(thread.guild.text_channels, name="grading-queue")
        if grading_channel:
            await grading_channel.send(
                f"📬 **New Group Submission**\n"
                f"📋 Assignment: {assignment['title']}\n"
                f"👥 Tim: {submission_data['team_name']}\n"
                f"🔗 Repo: {submission_data['repo_url']}\n"
                f"🔗 Deploy: {submission_data['deploy_url']}\n"
                f"📝 Job Desc: {submission_data['project_description']}\n\n"
                f"👥 Anggota:\n{members_info}"
            )

        logger.info(f"New group submission: {submission_data['team_name']} for assignment {assignment['title']}")