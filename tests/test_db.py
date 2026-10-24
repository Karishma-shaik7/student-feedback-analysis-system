"""
Unit tests for database helper functions and validation.
"""

from unittest.mock import MagicMock, patch
import pytest
import database.db as db_manager


def test_insert_feedback_rating_bounds():
    """Verify insert_feedback rejects out-of-range ratings before calling SQL."""
    # Rating 0
    ok, err = db_manager.insert_feedback(course_id=1, rating=0)
    assert ok is False
    assert "between 1 and 5" in err

    # Rating 6
    ok, err = db_manager.insert_feedback(course_id=1, rating=6)
    assert ok is False
    assert "between 1 and 5" in err

    # Non-integer rating
    ok, err = db_manager.insert_feedback(course_id=1, rating="abc")
    assert ok is False
    assert "Invalid rating" in err


def test_insert_feedback_unknown_course():
    """Verify insert_feedback rejects non-existent course ID."""
    with patch("database.db.get_course_by_id", return_value=None):
        ok, err = db_manager.insert_feedback(course_id=999, rating=5)
        assert ok is False
        assert "does not exist" in err


def test_check_db_connection_handles_failure():
    """Verify check_db_connection returns clean tuple without throwing."""
    with patch("database.db.get_db_cursor", side_effect=Exception("Connection refused")):
        healthy, msg = db_manager.check_db_connection()
        assert healthy is False
        assert "Database error" in msg or "Connection refused" in msg
