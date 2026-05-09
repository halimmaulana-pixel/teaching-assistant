"""Reminder scheduler for project ideas."""
import logging
import asyncio
import discord
from datetime import datetime

logger = logging.getLogger("teaching-assistant")

PROJECT_IDEAS = [
    "💻 **E-Commerce Platform** - Frontend: React + Tailwind, Backend: Node.js + Express, Database: PostgreSQL, Payment: Stripe",
    "🛒 **Marketplace Lokal** - Frontend: Next.js, Backend: Go + Gin, Database: MongoDB, Deploy: Vercel",
    "📚 **LMS (Learning Management System)** - Frontend: Vue.js + Nuxt, Backend: Laravel + MySQL, Database: Redis, CDN: Cloudflare",
    "🏥 **Sistem Rumah Sakit** - Frontend: React + Material UI, Backend: Spring Boot + PostgreSQL, Database: FHIR API",
    "🏋️ **Fitness Tracker App** - Frontend: Svelte + SvelteKit, Backend: FastAPI + SQLAlchemy, Database: PostgreSQL + TimescaleDB",
    "🍽️ **Restaurant Reservation** - Frontend: React + Chakra UI, Backend: Django + DRF, Database: PostgreSQL, Maps: Google Maps API",
    "🎓 **Quiz Platform** - Frontend: Angular + RxJS, Backend: Express + NestJS, Database: MongoDB, Real-time: Socket.io",
    "📝 **Project Management Tool** - Frontend: React + Redux Toolkit, Backend: Rails + PostgreSQL, Database: Elasticsearch",
    "🚗 **Rental Kendaraan** - Frontend: Next.js + Prisma, Backend: tRPC + Node.js, Database: PostgreSQL, Auth: Clerk",
    "🏠 **Property Listing** - Frontend: Gatsby + GraphQL, Backend: Python + Django, Database: PostgreSQL + Algolia",
    "💬 **Chat App Real-time** - Frontend: React + Socket.io Client, Backend: Node.js + Socket.io, Database: Redis + MongoDB",
    "📊 **Dashboard Analytics** - Frontend: React + Recharts, Backend: FastAPI + Pandas, Database: PostgreSQL + Grafana",
    "🎬 **Movie Streaming Platform** - Frontend: Vue 3 + Pinia, Backend: Go + gRPC, Database: PostgreSQL, CDN: AWS CloudFront",
    "🧗 **Outdoor Activity Booking** - Frontend: SvelteKit + Tailwind, Backend: Rust + Actix, Database: SQLite + Redis",
    "🌱 **Organic Food Delivery** - Frontend: Next.js + Stripe, Backend: Node.js + NestJS, Database: PostgreSQL + Prisma",
]

def get_reminder_message() -> str:
    """Generate reminder message with project ideas."""
    import random

    ideas_text = "\n".join([f"{i+1}. {idea}" for i, idea in enumerate(random.sample(PROJECT_IDEAS, min(5, len(PROJECT_IDEAS)))])

    message = f"""
⏰ **Reminder: Project Full Stack Web Programming**

Hai semuanya! 👋 Masih dalam proses brainstorming ide project web?

Berikut beberapa ide unik yang bisa kalian pertimbangkan:

{ideas_text}

📌 **Tips:**
• Pilih tech stack yang kalian Kuasai
• Pastikan bisa deploy (bisa pakai Vercel, Railway, Render gratis)
• Documentation penting untuk nilai tambahan

⏰ **Deadline: 13 Juni 2026**

Kirim ide kalian di channel kelas masing-masing ya!

#ProjectReminder #FullStackWeb
"""
    return message.strip()

async def send_reminder_to_umum(bot):
    """Send reminder to #umum channel."""
    guild = bot.client.get_guild(bot.guild_id)
    if not guild:
        return False

    channel = discord.utils.get(guild.text_channels, name="umum")
    if not channel:
        return False

    message = get_reminder_message()
    await channel.send(message)
    return True

async def start_reminder_scheduler(bot, interval_hours: int = 2):
    """Start the reminder scheduler."""
    logger.info(f"Reminder scheduler started - checking every {interval_hours} hours")

    while True:
        try:
            guild = bot.client.get_guild(bot.guild_id)
            if guild:
                channel = discord.utils.get(guild.text_channels, name="umum")
                if channel:
                    message = get_reminder_message()
                    await channel.send(message)
                    logger.info("Reminder sent to #umum")
                else:
                    logger.warning("Channel #umum not found")
            else:
                logger.warning("Guild not found")
        except Exception as e:
            logger.error(f"Error sending reminder: {e}")

        await asyncio.sleep(interval_hours * 3600)