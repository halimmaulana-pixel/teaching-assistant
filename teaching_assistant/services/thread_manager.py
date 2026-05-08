"""Thread management for assignment submissions."""
import logging
import discord

logger = logging.getLogger("teaching-assistant")

def slugify(title: str) -> str:
    """Convert title to thread-safe slug."""
    import re
    slug = title.lower().replace(" ", "-")
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    return slug[:50]

def format_thread_content(assignment: dict) -> str:
    """Format the thread post content with instructions."""
    deadline = assignment.get("deadline", "Belum ditentukan")
    grading_prompt = assignment.get("grading_prompt", "")

    content = f"""📋 **TUGAS: {assignment['title']}**

{assignment.get('description', 'Tidak ada deskripsi')}

⏰ **Deadline:** {deadline}

═══════════════════════════════════════
📝 **FORMAT SUBMISSION (WAJIB IKUTI):**
═══════════════════════════════════════

```
NIM: [your_nim]
---
[assignment content: link github, code, or explanation]
```

📎 **Allowed file types:**
   • Code: .py, .js, .php, .html, .css, .java, .cpp, .c, .rb, .go, .ts
   • Docs: .pdf, .txt, .md
   • Images: .png, .jpg, .jpeg, .gif, .webp
   • Archives: .zip (max 10MB)

⚠️ **IMPORTANT:**
• HANYA 1 SUBMISSION yang diterima (yang pertama)
• Submit EXACTLY sesuai format di atas
• NIM wajib ada di awal pesan

═══════════════════════════════════════"""
    if grading_prompt:
        content += f"\n📌 **Catatan Grading:**\n{grading_prompt}\n"

    return content.strip()

async def create_assignment_threads(guild, assignment: dict) -> dict:
    """Create threads for assignment in all class channels."""
    classes = assignment.get("classes", [])
    title_slug = slugify(assignment["title"])
    results = {}

    for class_channel_name in classes:
        class_channel = discord.utils.get(guild.text_channels, name=class_channel_name)
        if not class_channel:
            logger.warning(f"Channel not found: {class_channel_name}")
            results[class_channel_name] = {"status": "not_found"}
            continue

        thread_name = f"tugas-{title_slug}"
        try:
            thread = await class_channel.create_thread(
                name=thread_name,
                type=discord.ChannelType.public_thread,
                reason=f"Assignment: {assignment['title']}"
            )

            thread_content = format_thread_content(assignment)
            await thread.send(thread_content)

            results[class_channel_name] = {"status": "created", "thread_id": thread.id}
            logger.info(f"Thread created: {thread_name} in #{class_channel_name}")
        except Exception as e:
            logger.error(f"Failed to create thread in #{class_channel_name}: {e}")
            results[class_channel_name] = {"status": "error", "error": str(e)}

    return results