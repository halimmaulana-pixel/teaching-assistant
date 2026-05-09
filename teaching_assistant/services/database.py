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
                status TEXT DEFAULT 'active',
                assignment_type TEXT DEFAULT 'individual'
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
        await db.execute("""
            CREATE TABLE IF NOT EXISTS group_submissions (
                id TEXT PRIMARY KEY,
                assignment_id TEXT,
                team_name TEXT,
                repo_url TEXT,
                deploy_url TEXT,
                project_description TEXT,
                submitted_by_discord_id TEXT,
                submitted_by_name TEXT,
                class_channel TEXT,
                submitted_at TEXT,
                score INTEGER,
                feedback TEXT,
                graded_by TEXT,
                graded_at TEXT,
                FOREIGN KEY (assignment_id) REFERENCES assignments(id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS group_members (
                id TEXT PRIMARY KEY,
                submission_id TEXT,
                nim TEXT,
                role TEXT,
                FOREIGN KEY (submission_id) REFERENCES group_submissions(id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS server_members (
                discord_id TEXT PRIMARY KEY,
                username TEXT,
                nickname TEXT,
                display_name TEXT,
                roles TEXT,
                joined_at TEXT,
                synced_at TEXT,
                class_channel TEXT
            )
        """)
        await db.commit()

async def create_assignment(title: str, description: str, deadline: str,
                            classes: List[str], created_by: str,
                            grading_prompt: Optional[str] = None,
                            assignment_type: str = "individual") -> str:
    """Create a new assignment."""
    assignment_id = str(uuid4())
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT INTO assignments (id, title, description, deadline, classes, created_by, created_at, grading_prompt, status, assignment_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active', ?)
        """, (assignment_id, title, description, deadline, json.dumps(classes), created_by, datetime.now().isoformat(), grading_prompt, assignment_type))
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

async def create_group_submission(assignment_id: str, team_name: str, repo_url: str,
                                  deploy_url: str, project_description: str,
                                  submitted_by_discord_id: str, submitted_by_name: str,
                                  class_channel: str, members: List[dict]) -> str:
    """Create a new group submission with members."""
    submission_id = str(uuid4())
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT INTO group_submissions (id, assignment_id, team_name, repo_url, deploy_url, project_description, submitted_by_discord_id, submitted_by_name, class_channel, submitted_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (submission_id, assignment_id, team_name, repo_url, deploy_url, project_description, submitted_by_discord_id, submitted_by_name, class_channel, datetime.now().isoformat()))

        for member in members:
            member_id = str(uuid4())
            await db.execute("""
                INSERT INTO group_members (id, submission_id, nim, role)
                VALUES (?, ?, ?, ?)
            """, (member_id, submission_id, member["nim"], member["role"]))

        await db.commit()
    return submission_id

async def get_group_submission(submission_id: str) -> Optional[dict]:
    """Get group submission by ID with members."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute("SELECT * FROM group_submissions WHERE id = ?", (submission_id,)) as cursor:
            row = await cursor.fetchone()
            if not row:
                return None

        submission = {
            "id": row[0], "assignment_id": row[1], "team_name": row[2],
            "repo_url": row[3], "deploy_url": row[4], "project_description": row[5],
            "submitted_by_discord_id": row[6], "submitted_by_name": row[7],
            "class_channel": row[8], "submitted_at": row[9],
            "score": row[10], "feedback": row[11], "graded_by": row[12], "graded_at": row[13],
            "members": []
        }

        async with db.execute("SELECT * FROM group_members WHERE submission_id = ?", (submission_id,)) as cursor:
            async for member_row in cursor:
                submission["members"].append({
                    "id": member_row[0], "nim": member_row[2], "role": member_row[3]
                })

        return submission

async def check_group_submission_exists(assignment_id: str, team_name: str) -> bool:
    """Check if team already submitted for this assignment."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(
            "SELECT id FROM group_submissions WHERE assignment_id = ? AND team_name = ?",
            (assignment_id, team_name)
        ) as cursor:
            row = await cursor.fetchone()
            return row is not None

async def get_group_submissions_by_assignment(assignment_id: str, class_channel: str) -> List[dict]:
    """Get all group submissions for an assignment in a class."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(
            "SELECT * FROM group_submissions WHERE assignment_id = ? AND class_channel = ? ORDER BY submitted_at",
            (assignment_id, class_channel)
        ) as cursor:
            submissions = []
            async for row in cursor:
                submission_id = row[0]
                submission = {
                    "id": row[0], "assignment_id": row[1], "team_name": row[2],
                    "repo_url": row[3], "deploy_url": row[4], "project_description": row[5],
                    "submitted_by_discord_id": row[6], "submitted_by_name": row[7],
                    "class_channel": row[8], "submitted_at": row[9],
                    "score": row[10], "feedback": row[11], "graded_by": row[12], "graded_at": row[13],
                    "members": []
                }

                async with db.execute("SELECT * FROM group_members WHERE submission_id = ?", (submission_id,)) as member_cursor:
                    async for member_row in member_cursor:
                        submission["members"].append({
                            "id": member_row[0], "nim": member_row[2], "role": member_row[3]
                        })

                submissions.append(submission)
            return submissions

async def update_group_submission_grade(submission_id: str, score: int, feedback: str, graded_by: str):
    """Update group submission with grade."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            UPDATE group_submissions
            SET score = ?, feedback = ?, graded_by = ?, graded_at = ?
            WHERE id = ?
        """, (score, feedback, graded_by, datetime.now().isoformat(), submission_id))
        await db.commit()

async def get_assignment_by_thread_slug(thread_slug: str) -> Optional[dict]:
    """Get assignment by thread slug (title slugified)."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute("SELECT * FROM assignments WHERE status = 'active'",) as cursor:
            async for row in cursor:
                title_slug = slugify(row[1])
                individual_slug = f"tugas-{title_slug}"
                group_slug = f"tugas-kelompok-{title_slug}"
                if individual_slug == thread_slug or group_slug == thread_slug or title_slug in thread_slug:
                    assignment_type = row[9] if len(row) > 9 else "individual"
                    return {
                        "id": row[0], "title": row[1], "description": row[2], "deadline": row[3],
                        "classes": json.loads(row[4]) if row[4] else [], "created_by": row[5], "created_at": row[6],
                        "grading_prompt": row[7], "status": row[8], "assignment_type": assignment_type
                    }
    return None

async def upsert_server_member(discord_id: str, username: str, nickname: str,
                               display_name: str, roles: List[str],
                               joined_at: str, class_channel: str = None) -> None:
    """Insert or update a server member."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT INTO server_members (discord_id, username, nickname, display_name, roles, joined_at, synced_at, class_channel)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(discord_id) DO UPDATE SET
                username = excluded.username,
                nickname = excluded.nickname,
                display_name = excluded.display_name,
                roles = excluded.roles,
                synced_at = excluded.synced_at,
                class_channel = COALESCE(excluded.class_channel, server_members.class_channel)
        """, (discord_id, username, nickname, display_name, json.dumps(roles), joined_at, datetime.now().isoformat(), class_channel))
        await db.commit()

async def get_all_server_members() -> List[dict]:
    """Get all server members."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute("SELECT * FROM server_members ORDER BY username") as cursor:
            members = []
            async for row in cursor:
                members.append({
                    "discord_id": row[0], "username": row[1], "nickname": row[2],
                    "display_name": row[3], "roles": json.loads(row[4]) if row[4] else [],
                    "joined_at": row[5], "synced_at": row[6], "class_channel": row[7]
                })
            return members

async def get_server_member_count() -> int:
    """Get total count of synced server members."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM server_members") as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

async def get_members_by_role(role_name: str) -> List[dict]:
    """Get members with a specific role."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        members = []
        async with db.execute("SELECT * FROM server_members") as cursor:
            async for row in cursor:
                roles = json.loads(row[4]) if row[4] else []
                if role_name in roles:
                    members.append({
                        "discord_id": row[0], "username": row[1], "nickname": row[2],
                        "display_name": row[3], "roles": roles,
                        "joined_at": row[5], "synced_at": row[6], "class_channel": row[7]
                    })
        return members