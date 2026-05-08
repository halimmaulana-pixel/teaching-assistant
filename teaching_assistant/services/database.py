"""SQLite database operations for assignments and submissions."""
import aiosqlite
import json
import os
import re
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

async def get_all_assignments() -> List[dict]:
    """Get all assignments."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute("SELECT * FROM assignments ORDER BY created_at DESC") as cursor:
            assignments = []
            async for row in cursor:
                assignments.append({
                    "id": row[0], "title": row[1], "description": row[2], "deadline": row[3],
                    "classes": json.loads(row[4]) if row[4] else [], "created_by": row[5], "created_at": row[6],
                    "grading_prompt": row[7], "status": row[8]
                })
            return assignments

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

async def get_pending_submissions(assignment_id: str = None) -> List[dict]:
    """Get submissions without grades."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        if assignment_id:
            cursor = await db.execute("SELECT * FROM submissions WHERE score IS NULL AND assignment_id = ?", (assignment_id,))
        else:
            cursor = await db.execute("SELECT * FROM submissions WHERE score IS NULL")

        submissions = []
        async for row in cursor:
            submissions.append(parse_submission_row(row))
        return submissions

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
    slug = title.lower().replace(" ", "-")
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    return slug[:50]