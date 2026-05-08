# Teaching Assistant Bot - Design Specification

## Overview

**Project**: Teaching Assistant Bot (teaching-assistant)
**Purpose**: AI-powered Discord bot for managing and grading student assignments in Web Programming courses
**Core Functionality**: Dosen creates assignments via command → Bot auto-creates thread per class → Student submits in thread → AI (Claude) grades submissions → Feedback posted to thread

---

## Server Structure

```
Web Programming (Guild ID: 1468061169100263671)
├── #umum
├── #d1-si  → #rekap-d1-si
├── #c1-si  → #rekap-c1-si
├── #e1-si  → #rekap-e1-si
├── #g1-si  → #rekap-g1-si
├── #a2-si  → #rekap-a2-si
├── #h1-si  → #rekap-h1-si
├── #a1-si  → #rekap-a1-si
├── #b1-si  → #rekap-b1-si
├── #f1-si  → #rekap-f1-si
└── #rekap-umum
```

---

## User Roles

| Role | Actions |
|------|---------|
| **Dosen** | Create assignment, view stats, get recap |
| **Student** | Submit assignments in thread, view own grades |
| **Bot** | Detect submissions, call AI grading, post feedback |

---

## Core Features

### 1. Assignment Creation

**Command**: `!create-assignment` or via DM

**Parameters**:
- `title`: Assignment title
- `description`: Assignment details
- `deadline`: Due date/time (ISO format or natural language)
- `classes`: List of class channels to create threads for (e.g., `d1-si,c1-si,e1-si`)
- `grading_prompt`: Optional custom instructions for AI grader

**Flow**:
1. Dosen triggers command
2. Bot validates parameters
3. Bot creates thread in each class channel (e.g., `#d1-si/tugas-php-array`)
4. Bot posts thread with:
   - Title
   - Description
   - Deadline
   - **Submission format instructions** (MANDATORY)
5. Bot sends confirmation to Dosen

**Thread Content Template**:
```
📋 TUGAS: [title]

[description]

⏰ Deadline: [deadline]

═══════════════════════════════════════
📝 FORMAT SUBMISSION (WAJIB IKUTI):
═══════════════════════════════════════

NIM: [your_nim]
---
[assignment content: link github, code, or explanation]

📎 Allowed file types:
   Code: .py, .js, .php, .html, .css, .java, .cpp, .c, .rb, .go, .ts
   Docs: .pdf, .txt, .md
   Images: .png, .jpg, .jpeg, .gif, .webp
   Archives: .zip (max 10MB)

⚠️ IMPORTANT:
- HANYA 1 SUBMISSION yang diterima (yang pertama)
- Submit EXACTLY sesuai format di atas
- NIM wajib ada di awal pesan

═══════════════════════════════════════
```

### 2. Submission Detection

**Trigger**: New message in assignment thread

**Detection Logic**:
1. Bot monitors all class channels for new threads with prefix `tugas-`
2. When new message detected in such thread:
   - Check if message has attachment or code content
   - Validate student NIM format (required - posted at start of message)
   - Check if NIM already submitted (reject if duplicate)
   - Record submission with timestamp, user, content
   - React with ✅ to confirm receipt
3. Bot sends content to AI for grading

**Submission Format** (REQUIRED - posted at start of message in thread):
```
NIM: [your_nim]
--- (separator line) ---
[assignment content: link github, code, or explanation]
```

**Example Valid Submission**:
```
NIM: 2113456
---
Link Github: https://github.com/john123/tugas-php-array
Screenshot: https://i.imgur.com/abc.png
```

**File Format Restrictions**:
| Type | Allowed Extensions |
|------|-------------------|
| Code | `.py`, `.js`, `.php`, `.html`, `.css`, `.java`, `.cpp`, `.c`, `.rb`, `.go`, `.ts` |
| Documents | `.pdf`, `.txt`, `.md` |
| Images | `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp` |
| Archives | `.zip` (max 10MB) |

**Rejection Cases**:
| Case | Bot Response |
|------|--------------|
| No NIM in message | "❌ Format salah! Gunakan format: `NIM: [nim]`" |
| Duplicate submission (NIM already submitted) | "⚠️ Kamu sudah submit tugas ini. Hanya 1 submission yang diterima." |
| File type not allowed | "❌ File type tidak diizinkan. Allowed: .py, .js, .php, .html, .css, .pdf, .png, .jpg, .zip" |

### 3. AI Grading (Core Feature)

**Integration**: Bot as MCP server, Claude as MCP client

**Flow**:
1. Bot detects new submission (valid format)
2. Bot exposes `grade_submission(submission_id)` tool
3. AI (Claude) calls tool → receives submission content
4. AI analyzes and returns `{score, feedback, strengths, improvements}`
5. Bot posts grade to thread (PUBLIC in thread)

**Grading Response Format**:
```json
{
  "score": 85,
  "feedback": "Good logic in array manipulation. Consider adding error handling for edge cases.",
  "strengths": ["Correct array syntax", "Clear variable naming"],
  "improvements": ["Add input validation", "Handle empty array edge case"]
}
```

**Grade Posting Format** (in thread):
```
╔═══════════════════════════════════════╗
║  📊 GRADE RESULT                       ║
╠═══════════════════════════════════════╣
║  NIM: 2113456                          ║
║  Score: 85/100                        ║
║  ─────────────────────────────────     ║
║  ✅ Strengths:                         ║
║     • Correct array syntax             ║
║     • Clear variable naming            ║
║  ─────────────────────────────────     ║
║  📝 Feedback:                          ║
║  Good logic in array manipulation.    ║
║  Consider adding error handling.      ║
║  ─────────────────────────────────     ║
║  💡 Improvements:                     ║
║     • Add input validation            ║
║     • Handle empty array edge case    ║
║  ─────────────────────────────────     ║
║  Graded by: Claude AI                  ║
╚═══════════════════════════════════════╝
```

### 4. Stats & Recap

**Command**: `!stats [class]`

**Display** (posted in class channel):
```
📊 STATISTIK KELAS D1-SI
═══════════════════════════════════

📚 Assignment: Tugas PHP Array
⏰ Deadline: 2026-05-15 23:59

✅ SUDAH SUBMIT (8/12):
  1. 2113456 - John - 85/100 ⭐
  2. 2113457 - Sarah - 90/100 ⭐
  ...

❌ BELUM SUBMIT (4):
  1. 2113490 - Alice
  2. 2113491 - Bob
  ...

📈 RATA-RATA: 82.5
📅 Sisa waktu: 2 days
```

**Recap Channel**: `#rekap-d1-si`, etc.
- Daily/weekly summary posted automatically
- Include total submissions, avg scores, deadline status

### 5. Reminder System

**Automated Reminders** (posted in class channel):
- 1 day before deadline
- 1 hour before deadline
- After deadline (who didn't submit)

**Reminder Format**:
```
⏰ REMINDER: Tugas PHP Array
📅 Deadline: Hari ini jam 23:59
❌ Belum submit (4):
   1. 2113490 - Alice
   2. 2113491 - Bob
```

---

## Command Reference

| Command | Usage | Description |
|---------|-------|-------------|
| `!create-assignment` | `!create-assignment title:"..." desc:"..." deadline:"..." classes:"d1-si,c1-si"` | Create new assignment |
| `!stats` | `!stats d1-si` | Show class statistics |
| `!list-assignments` | `!list-assignments d1-si` | List all assignments |
| `!deadline` | `!deadline [assignment-id]` | Show deadline info |
| `!help` | `!help [command]` | Show help |
| `!mygrade` | `!mygrade [assignment-id]` | Student check own grade |

---

## Thread Naming Convention

```
tugas-{assignment-slug}
Example: tugas-php-array
```

---

## Data Model

### Assignment
```python
{
    "id": "uuid",
    "title": "string",
    "description": "string",
    "deadline": "datetime",
    "classes": ["d1-si", "c1-si"],  # JSON array
    "created_by": "discord_user_id",
    "created_at": "datetime",
    "grading_prompt": "string (optional)",
    "status": "active"  # 'active' | 'closed'
}
```

### Submission
```python
{
    "id": "uuid",
    "assignment_id": "uuid",
    "nim": "2113456",  # Student NIM
    "student_name": "John Doe",
    "student_discord_id": "discord_user_id",
    "class_channel": "d1-si",
    "content": "text or link",
    "attachments": ["url1", "url2"],  # JSON array
    "submitted_at": "datetime",
    "score": 85,  # NULL if not graded
    "feedback": "string",
    "strengths": ["array"],
    "improvements": ["error handling"],
    "graded_by": "Claude",
    "graded_at": "datetime"
}
```

---

## Technical Stack

- **Language**: Python 3.10+
- **Framework**: discord.py 2.x
- **MCP**: mcp Python SDK
- **Database**: SQLite (simple, file-based)
- **AI Integration**: Via MCP tools (Claude as client)
- **Dependencies**:
  - discord.py>=2.0.0
  - mcp>=1.0.0
  - aiohttp>=3.8.0
  - python-dotenv>=1.0.0
  - aiosqlite>=0.19.0

---

## Configuration

Environment variables:
```
DISCORD_TOKEN=xxx
DISCORD_GUILD_ID=1468061169100263671
DATABASE_PATH=./data/teaching_assistant.db
LOG_LEVEL=INFO
```

---

## Implementation Phases

### Phase 1: Core Infrastructure
- Project setup (pyproject.toml, structure)
- Discord bot connection
- SQLite database setup
- Basic command handler

### Phase 2: Assignment System
- `!create-assignment` command
- Thread creation per class
- Submission detection + validation

### Phase 3: AI Grading
- MCP server setup
- `grade_submission` tool
- Grade posting to thread

### Phase 4: Stats & Reminders
- `!stats` command
- Auto-recap to #rekap channels
- Reminder scheduler

---

## Decisions Summary

| Decision | Value |
|----------|-------|
| Student identification | NIM (not Discord username) |
| Submission limit | 1 per student per assignment |
| File formats | Code, docs, images, zip (10MB max) |
| Grade visibility | Public in thread |
| Late submission | To be determined (Phase 4) |
| Custom grading prompt | Optional per assignment |