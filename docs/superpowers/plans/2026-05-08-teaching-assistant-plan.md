# Teaching Assistant Bot - Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build AI-powered Discord bot for managing and grading student assignments in Web Programming courses

**Architecture:** Python-based Discord bot with SQLite database, using MCP protocol for AI grading integration. Bot monitors class channels for assignment threads, detects submissions, and exposes MCP tools for AI to grade.

**Tech Stack:** Python 3.10+, discord.py 2.x, MCP SDK, SQLite (aiosqlite), python-dotenv

---

## File Structure

```
teaching-assistant/
├── pyproject.toml
├── .env.example
├── src/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── bot.py               # Discord client, event handlers
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── assignment.py    # !create-assignment
│   │   ├── stats.py        # !stats
│   │   └── general.py      # !help, !list-assignments
│   ├── services/
│   │   ├── __init__.py
│   │   ├── database.py     # SQLite operations
│   │   ├── submission.py   # Submission detection
│   │   ├── thread_manager.py # Thread creation
│   │   └── grading.py      # MCP tools
│   └── utils/
│       ├── __init__.py
│       └── formatting.py   # Embed formatters
├── data/
├── tests/
│   ├── __init__.py
│   └── test_*.py
└── docs/superpowers/plans/
```

---

## Implementation Phases

### Phase 1: Core Infrastructure
### Phase 2: Assignment System
### Phase 3: AI Grading (MCP)
### Phase 4: Stats & Reminders

---

## Task 1: Project Setup & Configuration

**Files:**
- Create: `teaching-assistant/pyproject.toml`
- Create: `teaching-assistant/.env.example`
- Create: `teaching-assistant/src/__init__.py`
- Create: `teaching-assistant/src/main.py`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "teaching-assistant"
version = "0.1.0"
description = "AI-powered Discord bot for managing and grading student assignments"
requires-python = ">=3.10"
dependencies = [
    "discord.py>=2.0.0",
    "mcp>=1.0.0",
    "aiohttp>=3.8.0",
    "python-dotenv>=1.0.0",
    "aiosqlite>=0.19.0",
]

[project.scripts]
teaching-assistant = "teaching_assistant.main:main_sync"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["teaching_assistant"]
```

- [ ] **Step 2: Create .env.example**

```
DISCORD_TOKEN=your_bot_token_here
DISCORD_GUILD_ID=1468061169100263671
DATABASE_PATH=./data/teaching_assistant.db
LOG_LEVEL=INFO
```

- [ ] **Step 3: Create src/__init__.py**

```python
"""Teaching Assistant Bot - AI-powered assignment management for Discord."""
__version__ = "0.1.0"
```

- [ ] **Step 4: Create src/main.py**

```python
"""Entry point for Teaching Assistant Bot."""
import asyncio
import logging
import os
from dotenv import load_dotenv

load_dotenv()

from teaching_assistant.bot import Bot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("teaching-assistant")

async def main():
    """Run the bot."""
    logger.info("Starting Teaching Assistant Bot...")
    bot = Bot()
    await bot.run()

def main_sync():
    """Synchronous entry point."""
    asyncio.run(main())

if __name__ == "__main__":
    main_sync()
```

- [ ] **Step 5: Run verification**

```bash
cd teaching-assistant
python -c "from teaching_assistant.main import main_sync; print('Setup OK')"
```

- [ ] **Step 6: Commit**

```bash
git init && git add pyproject.toml .env.example src/
git commit -m "feat: project setup and configuration"
```

---

## Task 2: Bot Core & Database Setup

**Files:**
- Create: `teaching-assistant/src/bot.py`
- Create: `teaching-assistant/src/services/__init__.py`
- Create: `teaching-assistant/src/services/database.py`
- Create: `teaching-assistant/tests/test_database.py`

- [ ] **Step 1: Create src/bot.py**

```python
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
```

- [ ] **Step 2: Create src/services/database.py**

```python
"""SQLite database operations for assignments and submissions."""
import aiosqlite
import json
import os
from datetime import datetime
from typing import Optional, List
from uuid import uuid4

DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/teaching_assistant.db")

async def init_db():
    """Initialize database tables."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS assignments (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                deadline TEXT,
                classes TEXT,
                created_by TEXT,
                created_at TEXT,
                grading_prompt TEXT,
                status TEXT DEFAULT 'active'
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id TEXT PRIMARY KEY,
                assignment_id TEXT,
                nim TEXT,
                student_name TEXT,
                student_discord_id TEXT,
                class_channel TEXT,
                content TEXT,
                attachments TEXT,
                submitted_at TEXT,
                score INTEGER,
                feedback TEXT,
                strengths TEXT,
                improvements TEXT,
                graded_by TEXT,
                graded_at TEXT,
                FOREIGN KEY (assignment_id) REFERENCES assignments(id)
            )
        """)
        await db.commit()
        logger.info(f"Database initialized at {DATABASE_PATH}")

async def create_assignment(title: str, description: str, deadline: str,
                            classes: List[str], created_by: str,
                            grading_prompt: Optional[str] = None) -> str:
    """Create a new assignment."""
    assignment_id = str(uuid4())
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT INTO assignments (id, title, description, deadline, classes, created_by, created_at, grading_prompt, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active')
        """, (assignment_id, title, description, deadline, json.dumps(classes), created_by, datetime.now().isoformat(), grading_prompt))
        await db.commit()
    return assignment_id

async def get_assignment(assignment_id: str) -> Optional[dict]:
    """Get assignment by ID."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute("SELECT * FROM assignments WHERE id = ?", (assignment_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return {
                    "id": row[0], "title": row[1], "description": row[2], "deadline": row[3],
                    "classes": json.loads(row[4]), "created_by": row[5], "created_at": row[6],
                    "grading_prompt": row[7], "status": row[8]
                }
    return None

async def get_assignment_by_thread_slug(thread_slug: str) -> Optional[dict]:
    """Get assignment by thread slug (title slugified)."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute("SELECT * FROM assignments WHERE status = 'active'",) as cursor:
            async for row in cursor:
                title_slug = slugify(row[1])
                if f"tugas-{title_slug}" == thread_slug or title_slug in thread_slug:
                    return {
                        "id": row[0], "title": row[1], "description": row[2], "deadline": row[3],
                        "classes": json.loads(row[4]), "created_by": row[5], "created_at": row[6],
                        "grading_prompt": row[7], "status": row[8]
                    }
    return None

async def create_submission(assignment_id: str, nim: str, student_name: str,
                            student_discord_id: str, class_channel: str,
                            content: str, attachments: List[dict]) -> str:
    """Create a new submission."""
    submission_id = str(uuid4())
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT INTO submissions (id, assignment_id, nim, student_name, student_discord_id, class_channel, content, attachments, submitted_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (submission_id, assignment_id, nim, student_name, student_discord_id, class_channel, content, json.dumps(attachments), datetime.now().isoformat()))
        await db.commit()
    return submission_id

async def get_submission(submission_id: str) -> Optional[dict]:
    """Get submission by ID."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute("SELECT * FROM submissions WHERE id = ?", (submission_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return parse_submission_row(row)
    return None

async def get_submissions_by_assignment(assignment_id: str, class_channel: str) -> List[dict]:
    """Get all submissions for an assignment in a class."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(
            "SELECT * FROM submissions WHERE assignment_id = ? AND class_channel = ? ORDER BY submitted_at",
            (assignment_id, class_channel)
        ) as cursor:
            submissions = []
            async for row in cursor:
                submissions.append(parse_submission_row(row))
            return submissions

async def update_submission_grade(submission_id: str, score: int, feedback: str,
                                  strengths: List[str], improvements: List[str], graded_by: str):
    """Update submission with grade."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            UPDATE submissions 
            SET score = ?, feedback = ?, strengths = ?, improvements = ?, graded_by = ?, graded_at = ?
            WHERE id = ?
        """, (score, feedback, json.dumps(strengths), json.dumps(improvements), graded_by, datetime.now().isoformat(), submission_id))
        await db.commit()

async def check_submission_exists(assignment_id: str, nim: str) -> bool:
    """Check if student has already submitted for this assignment."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(
            "SELECT id FROM submissions WHERE assignment_id = ? AND nim = ?",
            (assignment_id, nim)
        ) as cursor:
            row = await cursor.fetchone()
            return row is not None

def parse_submission_row(row) -> dict:
    """Parse a submission row from database."""
    return {
        "id": row[0], "assignment_id": row[1], "nim": row[2], "student_name": row[3],
        "student_discord_id": row[4], "class_channel": row[5], "content": row[6],
        "attachments": json.loads(row[7]) if row[7] else [], "submitted_at": row[8],
        "score": row[9], "feedback": row[10], "strengths": json.loads(row[11]) if row[11] else [],
        "improvements": json.loads(row[12]) if row[12] else [], "graded_by": row[13], "graded_at": row[14]
    }

def slugify(title: str) -> str:
    """Convert title to thread-safe slug."""
    import re
    slug = title.lower().replace(" ", "-")
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    return slug[:50]
```

- [ ] **Step 3: Create tests/test_database.py**

```python
"""Tests for database operations."""
import pytest
import os
import tempfile
from teaching_assistant.services.database import init_db, create_assignment, get_assignment, check_submission_exists

@pytest.fixture
async def test_db():
    """Create temporary test database."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.environ["DATABASE_PATH"] = path
    await init_db()
    yield path
    os.unlink(path)

@pytest.mark.asyncio
async def test_create_and_get_assignment(test_db):
    """Test creating and retrieving an assignment."""
    assignment_id = await create_assignment(
        title="Test Assignment",
        description="Test description",
        deadline="2026-05-15 23:59",
        classes=["d1-si", "c1-si"],
        created_by="dosen123"
    )
    assert assignment_id is not None
    assert len(assignment_id) == 36

    assignment = await get_assignment(assignment_id)
    assert assignment is not None
    assert assignment["title"] == "Test Assignment"
    assert assignment["classes"] == ["d1-si", "c1-si"]

@pytest.mark.asyncio
async def test_check_submission_exists(test_db):
    """Test duplicate submission check."""
    assignment_id = await create_assignment(
        title="Test Assignment",
        description="Test description",
        deadline="2026-05-15 23:59",
        classes=["d1-si"],
        created_by="dosen123"
    )
    
    exists = await check_submission_exists(assignment_id, "2113456")
    assert exists == False
```

- [ ] **Step 4: Run tests**

```bash
cd teaching-assistant
pytest tests/test_database.py -v
```

- [ ] **Step 5: Commit**

```bash
git add src/bot.py src/services/
git commit -m "feat: bot core and database setup"
```

---

## Task 3: Assignment Command & Thread Creation

**Files:**
- Create: `teaching-assistant/src/commands/__init__.py`
- Create: `teaching-assistant/src/commands/assignment.py`
- Create: `teaching-assistant/src/services/thread_manager.py`

- [ ] **Step 1: Create src/services/thread_manager.py**

```python
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
```

- [ ] **Step 2: Create src/commands/assignment.py**

```python
"""Assignment creation commands."""
import re
import logging
from discord import Embed

logger = logging.getLogger("teaching-assistant")

def parse_assignment_command(content: str) -> dict:
    """Parse !create-assignment command arguments."""
    pattern = r'(\w+):"([^"]*)"|(\w+):([^\s]+)'
    matches = re.findall(pattern, content)
    
    result = {}
    for m in matches:
        key = m[0] or m[2]
        value = m[1] or m[3]
        result[key] = value
    
    return result

async def handle_create_assignment(message, bot_instance):
    """Handle !create-assignment command."""
    content = message.content
    if not content.startswith("!create-assignment"):
        return
    
    args = parse_assignment_command(content)
    
    required = ["title", "deadline", "classes"]
    missing = [k for k in required if k not in args]
    if missing:
        await message.reply(f"❌ Missing required fields: {', '.join(missing)}\n\nUsage:\n```!create-assignment title:\"...\" deadline:\"...\" classes:\"d1-si,c1-si\"```")
        return
    
    classes = [c.strip() for c in args["classes"].split(",")]
    
    from teaching_assistant.services.database import create_assignment, init_db
    await init_db()
    
    assignment = {
        "title": args["title"],
        "description": args.get("desc", ""),
        "deadline": args["deadline"],
        "classes": classes,
        "grading_prompt": args.get("grading_prompt", ""),
        "created_by": str(message.author.id)
    }
    
    assignment_id = await create_assignment(**assignment)
    assignment["id"] = assignment_id
    
    guild = message.guild
    from teaching_assistant.services.thread_manager import create_assignment_threads
    results = await create_assignment_threads(guild, assignment)
    
    success = [k for k, v in results.items() if v["status"] == "created"]
    failed = [k for k, v in results.items() if v["status"] != "created"]
    
    response = f"✅ Assignment created: **{assignment['title']}**\n\n📁 Threads created in: {', '.join(success) if success else 'none'}"
    if failed:
        response += f"\n❌ Failed: {', '.join(failed)}"
    
    await message.reply(response)
```

- [ ] **Step 3: Create src/commands/__init__.py**

```python
"""Commands for Teaching Assistant Bot."""
```

- [ ] **Step 4: Update bot.py command handler**

```python
async def handle_message(self, message: discord.Message):
    """Handle incoming messages."""
    if message.author.bot:
        return
    
    content = message.content.strip()
    
    if content.startswith("!create-assignment"):
        from teaching_assistant.commands.assignment import handle_create_assignment
        await handle_create_assignment(message, self)
```

- [ ] **Step 5: Commit**

```bash
git add src/commands/ src/services/thread_manager.py
git commit -m "feat: assignment command and thread creation"
```

---

## Task 4: Submission Detection & Validation

**Files:**
- Create: `teaching-assistant/src/services/submission.py`
- Create: `teaching-assistant/tests/test_submission.py`
- Modify: `teaching-assistant/src/bot.py`

- [ ] **Step 1: Create src/services/submission.py**

```python
"""Submission detection and validation."""
import re
import logging
from typing import Optional, Tuple, List

logger = logging.getLogger("teaching-assistant")

VALID_EXTENSIONS = {
    "code": [".py", ".js", ".php", ".html", ".css", ".java", ".cpp", ".c", ".rb", ".go", ".ts"],
    "docs": [".pdf", ".txt", ".md"],
    "images": [".png", ".jpg", ".jpeg", ".gif", ".webp"],
    "archives": [".zip"]
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def extract_nim(content: str) -> Optional[str]:
    """Extract NIM from submission content."""
    match = re.search(r"^NIM:\s*(\S+)", content, re.MULTILINE)
    return match.group(1) if match else None

def extract_content_after_nim(content: str) -> str:
    """Get content after NIM line."""
    parts = content.split("---", 1)
    return parts[1].strip() if len(parts) > 1 else content

def validate_submission_format(content: str) -> Tuple[bool, Optional[str]]:
    """Validate submission format. Returns (is_valid, error_message)."""
    if not content or not content.strip():
        return False, "Konten kosong"
    
    nim = extract_nim(content)
    if not nim:
        return False, "❌ Format salah! Gunakan format:\n```\nNIM: [nim]\n---\n[content]\n```"
    
    if len(nim) < 4 or len(nim) > 20:
        return False, "❌ NIM tidak valid (harus 4-20 karakter)"
    
    return True, None

def validate_attachments(attachments: List[dict]) -> Tuple[bool, Optional[str]]:
    """Validate attachment file types and sizes."""
    if not attachments:
        return True, None
    
    all_exts = [ext for exts in VALID_EXTENSIONS.values() for ext in exts]
    
    for att in attachments:
        filename = att.get("filename", "")
        size = att.get("size", 0)
        
        ext = "." + filename.split(".")[-1].lower() if "." in filename else ""
        
        if ext not in all_exts:
            allowed = ", ".join(all_exts)
            return False, f"❌ File type tidak diizinkan: {ext}\nAllowed: {allowed}"
        
        if size > MAX_FILE_SIZE:
            return False, f"❌ File terlalu besar: {filename} (max 10MB)"
    
    return True, None

def parse_submission(message) -> dict:
    """Parse a Discord message into submission data."""
    return {
        "nim": extract_nim(message.content),
        "content": extract_content_after_nim(message.content),
        "attachments": [
            {
                "filename": att.filename,
                "url": att.url,
                "content_type": att.content_type,
                "size": att.size
            }
            for att in message.attachments
        ]
    }
```

- [ ] **Step 2: Create tests/test_submission.py**

```python
"""Tests for submission validation."""
import pytest
from teaching_assistant.services.submission import (
    extract_nim, validate_submission_format, validate_attachments
)

def test_extract_nim():
    """Test NIM extraction."""
    assert extract_nim("NIM: 2113456\n---\ncontent") == "2113456"
    assert extract_nim("NIM:ABC123\n---\ntest") == "ABC123"
    assert extract_nim("No NIM here") is None

def test_validate_submission_format():
    """Test format validation."""
    valid_content = "NIM: 2113456\n---\nhttps://github.com/test"
    is_valid, error = validate_submission_format(valid_content)
    assert is_valid == True
    assert error is None
    
    is_valid, error = validate_submission_format("No NIM")
    assert is_valid == False
    assert "Format salah" in error

def test_validate_attachments():
    """Test attachment validation."""
    valid_files = [{"filename": "test.py", "size": 1000}]
    is_valid, error = validate_attachments(valid_files)
    assert is_valid == True
    
    invalid_files = [{"filename": "test.exe", "size": 1000}]
    is_valid, error = validate_attachments(invalid_files)
    assert is_valid == False
```

- [ ] **Step 3: Update bot.py submission handler**

```python
async def handle_message(self, message: discord.Message):
    """Handle incoming messages."""
    if message.author.bot:
        return
    
    # Check if message is in a thread (submission)
    if isinstance(message.channel, discord.Thread):
        thread_name = message.channel.name
        if thread_name.startswith("tugas-"):
            await self.handle_submission(message, message.channel)
            return
    
    # Handle commands
    content = message.content.strip()
    if content.startswith("!create-assignment"):
        from teaching_assistant.commands.assignment import handle_create_assignment
        await handle_create_assignment(message, self)

async def handle_submission(self, message: discord.Message, thread: discord.Thread):
    """Handle assignment submission in thread."""
    from teaching_assistant.services.submission import validate_submission_format, validate_attachments, parse_submission
    from teaching_assistant.services.database import init_db, get_assignment_by_thread_slug, check_submission_exists, create_submission
    
    await init_db()
    
    # Validate format
    is_valid, error = validate_submission_format(message.content)
    if not is_valid:
        await thread.send(error)
        return
    
    # Parse submission
    submission_data = parse_submission(message)
    nim = submission_data["nim"]
    
    # Validate attachments
    is_valid, error = validate_attachments(submission_data["attachments"])
    if not is_valid:
        await thread.send(error)
        return
    
    # Get assignment from thread name
    assignment = await get_assignment_by_thread_slug(thread.name)
    if not assignment:
        logger.warning(f"No assignment found for thread: {thread.name}")
        return
    
    # Check for duplicate submission
    exists = await check_submission_exists(assignment["id"], nim)
    if exists:
        await thread.send("⚠️ Kamu sudah submit tugas ini. Hanya 1 submission yang diterima.")
        return
    
    # Save submission
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
```

- [ ] **Step 4: Commit**

```bash
git add src/services/submission.py tests/
git commit -m "feat: submission detection and validation"
```

---

## Task 5: MCP Server & AI Grading

**Files:**
- Create: `teaching-assistant/src/services/grading.py`
- Create: `teaching-assistant/src/mcp_server.py`
- Modify: `teaching-assistant/pyproject.toml`

- [ ] **Step 1: Create src/services/grading.py**

```python
"""Grading service - formats grade output for Discord."""
import logging

logger = logging.getLogger("teaching-assistant")

def format_grade_embed(submission: dict, assignment_title: str) -> dict:
    """Format grade result as Discord embed."""
    score = submission.get("score", 0)
    feedback = submission.get("feedback", "")
    strengths = submission.get("strengths", [])
    improvements = submission.get("improvements", [])
    nim = submission.get("nim", "Unknown")
    
    # Color based on score
    if score >= 80:
        color = 0x00FF00  # Green
    elif score >= 60:
        color = 0xFFFF00  # Yellow
    else:
        color = 0xFF0000  # Red
    
    embed = {
        "title": f"📊 Grade Result - {assignment_title}",
        "color": color,
        "fields": [
            {"name": "NIM", "value": nim, "inline": True},
            {"name": "Score", "value": f"{score}/100", "inline": True},
        ]
    }
    
    if strengths:
        strength_text = "\n".join([f"✅ {s}" for s in strengths])
        embed["fields"].append({"name": "Strengths", "value": strength_text, "inline": False})
    
    if feedback:
        embed["fields"].append({"name": "Feedback", "value": feedback, "inline": False})
    
    if improvements:
        improve_text = "\n".join([f"💡 {i}" for i in improvements])
        embed["fields"].append({"name": "Improvements", "value": improve_text, "inline": False})
    
    return embed
```

- [ ] **Step 2: Create src/mcp_server.py**

```python
"""MCP server for AI grading integration."""
import logging
from mcp.server import Server
from mcp.types import Tool, TextContent

logger = logging.getLogger("teaching-assistant")

server = Server("teaching-assistant-grading")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List grading tools available to AI."""
    return [
        Tool(
            name="get_pending_submissions",
            description="Get all submissions that need grading",
            inputSchema={
                "type": "object",
                "properties": {
                    "assignment_id": {"type": "string", "description": "Assignment ID to filter by"}
                }
            }
        ),
        Tool(
            name="get_submission_content",
            description="Get the full content of a submission for grading",
            inputSchema={
                "type": "object",
                "properties": {
                    "submission_id": {"type": "string", "description": "The submission ID"}
                },
                "required": ["submission_id"]
            }
        ),
        Tool(
            name="submit_grade",
            description="Submit the grading result for a submission",
            inputSchema={
                "type": "object",
                "properties": {
                    "submission_id": {"type": "string"},
                    "score": {"type": "integer", "minimum": 0, "maximum": 100},
                    "feedback": {"type": "string"},
                    "strengths": {"type": "array", "items": {"type": "string"}},
                    "improvements": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["submission_id", "score", "feedback"]
            }
        ),
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls from AI."""
    if name == "get_pending_submissions":
        return await get_pending_submissions(arguments.get("assignment_id"))
    elif name == "get_submission_content":
        return await get_submission_content(arguments["submission_id"])
    elif name == "submit_grade":
        return await submit_grade(arguments)
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

async def get_pending_submissions(assignment_id: str = None) -> list[TextContent]:
    """Get submissions pending grading."""
    from teaching_assistant.services.database import get_pending_submissions_from_db
    
    submissions = await get_pending_submissions_from_db(assignment_id)
    
    if not submissions:
        return [TextContent(type="text", text="No pending submissions")]
    
    result = "📋 Pending Submissions:\n\n"
    for sub in submissions:
        result += f"- ID: {sub['id']}\n"
        result += f"  NIM: {sub['nim']}\n"
        result += f"  Content: {sub['content'][:100]}...\n"
        result += f"  Attachments: {len(sub['attachments'])}\n\n"
    
    return [TextContent(type="text", text=result)]

async def get_submission_content(submission_id: str) -> list[TextContent]:
    """Get full submission content for grading."""
    from teaching_assistant.services.database import get_submission
    
    submission = await get_submission(submission_id)
    
    if not submission:
        return [TextContent(type="text", text=f"Submission not found: {submission_id}")]
    
    result = f"## Submission: {submission_id}\n\n"
    result += f"**NIM:** {submission['nim']}\n"
    result += f"**Student:** {submission['student_name']}\n"
    result += f"**Class:** {submission['class_channel']}\n"
    result += f"**Submitted:** {submission['submitted_at']}\n\n"
    result += f"## Content:\n{submission['content']}\n\n"
    
    if submission['attachments']:
        result += "## Attachments:\n"
        for att in submission['attachments']:
            result += f"- {att['filename']}: {att['url']}\n"
    
    return [TextContent(type="text", text=result)]

async def submit_grade(arguments: dict) -> list[TextContent]:
    """Submit grading result."""
    from teaching_assistant.services.database import update_submission_grade
    
    await update_submission_grade(
        submission_id=arguments["submission_id"],
        score=arguments["score"],
        feedback=arguments["feedback"],
        strengths=arguments.get("strengths", []),
        improvements=arguments.get("improvements", []),
        graded_by="Claude AI"
    )
    
    logger.info(f"Grade submitted for {arguments['submission_id']}: {arguments['score']}/100")
    
    return [TextContent(type="text", text=f"✅ Grade submitted: {arguments['score']}/100")]
```

- [ ] **Step 3: Update database.py with new functions**

```python
async def get_pending_submissions_from_db(assignment_id: str = None) -> List[dict]:
    """Get submissions without grades."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        if assignment_id:
            query = "SELECT * FROM submissions WHERE score IS NULL AND assignment_id = ?"
            cursor = await db.execute(query, (assignment_id,))
        else:
            query = "SELECT * FROM submissions WHERE score IS NULL"
            cursor = await db.execute(query)
        
        submissions = []
        async for row in cursor:
            submissions.append(parse_submission_row(row))
        return submissions
```

- [ ] **Step 4: Commit**

```bash
git add src/mcp_server.py src/services/grading.py
git commit -m "feat: MCP server for AI grading"
```

---

## Task 6: Stats Command & Reminders

**Files:**
- Create: `teaching-assistant/src/commands/stats.py`
- Create: `teaching-assistant/src/commands/general.py`
- Create: `teaching-assistant/src/services/reminder.py`
- Modify: `teaching-assistant/src/bot.py`

- [ ] **Step 1: Create src/commands/stats.py**

```python
"""Stats command for viewing class statistics."""
import logging
from discord import Embed

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
```

- [ ] **Step 2: Create src/commands/general.py**

```python
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
```

- [ ] **Step 3: Create src/services/reminder.py**

```python
"""Reminder system for deadlines."""
import logging
import asyncio
from datetime import datetime, timedelta

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
        
        # 24 hours before
        if timedelta(hours=23) <= time_diff <= timedelta(hours=24):
            await send_reminder(bot, assignment, "24 hours")
        
        # 1 hour before
        elif timedelta(minutes=59) <= time_diff <= timedelta(hours=1):
            await send_reminder(bot, assignment, "1 hour")
        
        # Just passed deadline
        elif timedelta(hours=-1) <= time_diff < timedelta(0):
            await send_deadline_passed(bot, assignment)

def parse_deadline(deadline_str: str) -> datetime:
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
```

- [ ] **Step 4: Commit**

```bash
git add src/commands/stats.py src/commands/general.py src/services/reminder.py
git commit -m "feat: stats command and reminder system"
```

---

## Self-Review Checklist

- [ ] Spec coverage: All features in design spec have tasks
- [ ] No placeholders: All steps have actual code
- [ ] Type consistency: Function signatures match across tasks
- [ ] File paths: All paths are correct for new project structure

**Spec Coverage:**
| Spec Section | Task |
|--------------|------|
| Assignment Creation | Task 3 |
| Thread Creation | Task 3 |
| Submission Detection | Task 4 |
| NIM Validation | Task 4 |
| File Validation | Task 4 |
| MCP Grading | Task 5 |
| Stats Command | Task 6 |
| Reminders | Task 6 |

---

## Execution Options

**Plan complete and saved to** `docs/superpowers/plans/2026-05-08-teaching-assistant-plan.md`

**Two execution options:**

1. **Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

2. **Inline Execution** - Execute tasks in this session using executing-plans

**Which approach?**