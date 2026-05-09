"""Reminder scheduler for project ideas."""
import logging
import asyncio
import discord
from datetime import datetime

logger = logging.getLogger("teaching-assistant")

PROJECT_IDEAS = [
    "📈 **Indonesian Commodity Price Tracker** - Frontend: Next.js + Tailwind, Backend: FastAPI + BeautifulSoup, Database: PostgreSQL, Data: Scraping BPS/Pasarpedia - Pantau harga beras, cabai, bawang real-time",
    "🎓 **Indonesian Scholarship Aggregator** - Frontend: React + Prisma, Backend: Node.js + Express, Database: MongoDB, Data: Scraping LPDP/Kemdikbud - Kumpulkan semua scholarship, filter by requirements, deadline tracker",
    "✈️ **Flight Price Hunter (Indonesia-focus)** - Frontend: Next.js + Recharts, Backend: Django + Scrapy, Database: PostgreSQL, Data: Tiket.com/Traveloka - Price history, alert when drops, predict best time to buy",
    "📰 **News Aggregator for Tech Topics** - Frontend: Svelte + SvelteKit, Backend: FastAPI + Redis, Database: PostgreSQL, Data: RSS/CNN/Detik - AI summarize news, sentiment analysis, topic clustering",
    "💼 **Indonesia Job Portal Aggregator** - Frontend: React + Redux, Backend: Laravel + PostgreSQL, Database: PostgreSQL, Data: Scraping Jobstreet/Glints/LinkedIn - Filter salary, remote-friendly, startup-only jobs",
    "📱 **Local Event Discovery (Indonesia)** - Frontend: Next.js + Leaflet Maps, Backend: Go + GORM, Database: PostgreSQL, Data: Goers/Eventory API - Filter by city, free/paid, category, map-based discovery",
    "📊 **Cryptocurrency & IHSG Dashboard** - Frontend: Vue 3 + Chart.js, Backend: Node.js + Socket.io, Database: InfluxDB, Data: CoinGecko/Yahoo Finance API - Portfolio tracker, alerts, technical indicators",
    "🌾 **Indonesian Food Price Predictor** - Frontend: React + Material UI, Backend: FastAPI + Scikit-learn, Database: PostgreSQL, Data: data.go.id - ML predict price movement, benefit analysis untuk consumers",
    "🏗️ **Construction Material Price Monitor** - Frontend: Next.js + D3.js, Backend: Spring Boot + WebSocket, Database: PostgreSQL, Data: Scraping harga besi/semen - Real-time alerts, historical trends, prediction",
    "⚡ **Peer-to-Peer Energy Sharing** - Frontend: React + Tailwind, Backend: Node.js + MQTT, Database: InfluxDB, Data: Smart meter APIs - Share solar energy antar rumah tangga, smart grid tracking",
    "📚 **Secondhand Book Exchange** - Frontend: SvelteKit + Leaflet, Backend: Express + MongoDB, Database: MongoDB, Data: Open Library API - Tukar buku bekas, location-based matching, sustainability",
    "🌊 **Maritime Cargo Tracker (Indonesia)** - Frontend: Vue.js + Mapbox, Backend: Go + gRPC, Database: PostgreSQL, Data: Shipping APIs - Tracking kapal kargo, estimasi arrival, port monitoring",
    "📋 **Tabungan Kelompok (Group Savings)** - Frontend: React + Tailwind, Backend: Node.js + Express, Database: PostgreSQL, Data: Real-time updates - Community savings, transparent voting for spending",
    "🎯 **Skill Exchange Network** - Frontend: Next.js + Prisma, Backend: Django + DRF, Database: PostgreSQL, Data: User profiles - Tukar skill (coding↔design), matching system, review",
]

def get_reminder_message() -> str:
    """Generate reminder message with project ideas."""
    import random

    ideas_text = "\n".join([f"{i+1}. {idea}" for i, idea in enumerate(random.sample(PROJECT_IDEAS, min(5, len(PROJECT_IDEAS))))])

    message = f"""
⏰ **Reminder: Project Full Stack Web Programming**

Hai semuanya! 👋 Still brainstorming for project ideas?

Berikut ide-ide yang utilize PUBLIC DATA dari internet:

{ideas_text}

📌 **Tips:**
• Pilih yang sesuai skill + passion
• Public data bisa dari API, web scraping, atau open data Indonesia
• Bisa deploy di Vercel/Railway/Netlify (gratis!)
• Tech stack boleh berbeda dari rekomendasi di atas

⏰ **Deadline: 13 Juni 2026**

Kirim ide kalian di channel kelas masing-masing ya!

#ProjectReminder #PublicData #FullStackWeb
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