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


def test_schema_sql_is_non_destructive_and_db_agnostic():
    """Verify schema.sql never drops tables and has no hardcoded database name."""
    from pathlib import Path
    schema_path = Path(__file__).resolve().parent.parent / "database" / "schema.sql"
    assert schema_path.exists()
    content = schema_path.read_text(encoding="utf-8")

    # Safety checks
    assert "DROP TABLE" not in content.upper(), "schema.sql must NEVER contain DROP TABLE"
    assert "DROP DATABASE" not in content.upper(), "schema.sql must NEVER contain DROP DATABASE"
    assert "USE " not in content.upper(), "schema.sql must not hardcode USE <database>"
    assert "CREATE DATABASE" not in content.upper(), "schema.sql must not hardcode CREATE DATABASE"

    # Required idempotent DDL
    assert "CREATE TABLE IF NOT EXISTS courses" in content
    assert "CREATE TABLE IF NOT EXISTS feedback" in content
    assert "INSERT IGNORE INTO courses" in content


def test_init_db_targets_configured_database():
    """Verify init_db connects directly to the specified database (e.g. defaultdb)."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch("database.db.get_db_connection") as mock_get_conn:
        mock_get_conn.return_value = mock_conn

        ok, msg = db_manager.init_db(database_name="defaultdb")
        assert ok is True
        assert "defaultdb" in msg

        # Verify get_db_connection was called targeting defaultdb
        mock_get_conn.assert_any_call(database_override="defaultdb", use_database=True)

        # Verify all executed statements are non-destructive
        for call_item in mock_cursor.execute.call_args_list:
            stmt = call_item[0][0].upper()
            assert not stmt.startswith("DROP "), f"Destructive statement found: {stmt}"
            assert not stmt.startswith("DELETE "), f"Delete statement found: {stmt}"


def test_get_all_courses_auto_inits_on_missing_table():
    """Verify get_all_courses recovers automatically when table 'courses' does not exist yet."""
    from mysql.connector import Error, errorcode

    table_missing_err = Error(msg="Table 'defaultdb.courses' doesn't exist", errno=errorcode.ER_NO_SUCH_TABLE)

    mock_cursor = MagicMock()
    # First attempt fails with 1146 (no such table), second attempt succeeds
    mock_cursor.fetchall.return_value = [
        {"id": 1, "course_code": "CS101", "course_name": "Intro CS", "instructor_name": "Turing", "department": "CS"}
    ]

    with patch("database.db.get_db_cursor") as mock_cursor_ctx, \
         patch("database.db.init_db", return_value=(True, "Initialized")) as mock_init:

        # Setup side_effects: first context manager raises Error 1146, second succeeds
        cm_fail = MagicMock()
        cm_fail.__enter__.side_effect = table_missing_err

        cm_success = MagicMock()
        cm_success.__enter__.return_value = (mock_cursor, None)

        mock_cursor_ctx.side_effect = [cm_fail, cm_success]

        courses = db_manager.get_all_courses()

        # init_db must have been invoked to heal the missing table
        mock_init.assert_called_once()
        assert len(courses) == 1
        assert courses[0]["course_code"] == "CS101"
