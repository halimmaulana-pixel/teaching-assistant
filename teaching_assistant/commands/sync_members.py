"""Command to sync all Discord server members to local database."""
import logging
import discord

logger = logging.getLogger("teaching-assistant")

CLASS_CHANNEL_NAMES = ["d1-si", "c1-si", "e1-si", "g1-si", "a2-si", "h1-si", "a1-si", "b1-si", "f1-si"]

async def handle_sync_members(message: discord.Message, bot):
    """Sync all server members to local database."""
    from teaching_assistant.services.database import (
        init_db, upsert_server_member, get_server_member_count
    )

    await init_db()

    guild = bot.client.get_guild(bot.guild_id)
    if not guild:
        await message.reply("❌ Guild not found. Bot mungkin belum terhubung ke server.")
        return

    await message.reply("🔄 Memulai sync server members...")

    synced_count = 0
    error_count = 0
    class_channel_count = 0

    try:
        await message.reply("🔄 Fetching members dari Discord...")

        async def fetch_members():
            """Fetch all members from guild."""
            members_list = []
            async for member in guild.config.fetch_members(limit=150):
                members_list.append(member)
            return members_list

        members = await fetch_members()
        await message.reply(f"🔄 Found **{len(members)}** members. Starting sync...")

        for member in members:
            if member.bot:
                continue

            roles = [role.name for role in member.roles if role.name != "@everyone"]

            class_channel = None
            for channel_name in CLASS_CHANNEL_NAMES:
                if any(channel_name.lower() in role.lower() for role in roles):
                    class_channel = channel_name
                    class_channel_count += 1
                    break

            try:
                await upsert_server_member(
                    discord_id=str(member.id),
                    username=member.name,
                    nickname=member.nick or "",
                    display_name=member.display_name,
                    roles=roles,
                    joined_at=member.joined_at.isoformat() if member.joined_at else "",
                    class_channel=class_channel
                )
                synced_count += 1
            except Exception as e:
                logger.error(f"Error syncing member {member.name}: {e}")
                error_count += 1

        total_members = await get_server_member_count()

        embed = discord.Embed(
            title="✅ Sync Completed",
            color=discord.Color.green()
        )
        embed.add_field(
            name="Results",
            value=f"✅ Synced: **{synced_count}** members\n"
                  f"⚠️ Errors: **{error_count}**\n"
                  f"📋 Total in DB: **{total_members}** members",
            inline=False
        )
        embed.add_field(
            name="Class Breakdown",
            value=f"🎓 Members with class role: **{class_channel_count}**",
            inline=False
        )

        embed.set_footer(text="Use !list-members to see all synced members")

        await message.reply(embed=embed)

    except Exception as e:
        logger.error(f"Sync error: {e}")
        await message.reply(f"❌ Error during sync: {str(e)}")
