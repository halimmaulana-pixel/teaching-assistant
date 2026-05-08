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