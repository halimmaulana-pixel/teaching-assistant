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