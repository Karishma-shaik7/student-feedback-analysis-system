"""
Pytest configuration and test fixtures.
Provides test client, mock data, and database mocks for isolated automated testing.
"""

import pytest
from unittest.mock import MagicMock, patch
from app import create_app
import database.db as db_manager


@pytest.fixture
def app():
    """Creates a Flask application instance configured for testing."""
    test_app = create_app("testing")
    test_app.config["TESTING"] = True
    test_app.config["WTF_CSRF_ENABLED"] = False
    return test_app


@pytest.fixture
def client(app):
    """Provides a test client for simulating HTTP requests."""
    return app.test_client()


@pytest.fixture
def sample_courses():
    """Standard sample course records for tests."""
    return [
        {"id": 1, "course_code": "CS101", "course_name": "Introduction to Computer Science", "instructor_name": "Dr. Alan Turing", "department": "Computer Science"},
        {"id": 2, "course_code": "CS201", "course_name": "Data Structures and Algorithms", "instructor_name": "Dr. Ada Lovelace", "department": "Computer Science"},
        {"id": 3, "course_code": "CS301", "course_name": "Database Management Systems", "instructor_name": "Dr. Edgar Codd", "department": "Computer Science"},
    ]


@pytest.fixture
def sample_feedback():
    """Standard feedback records for analytics tests."""
    return [
        {"id": 1, "course_id": 1, "course_code": "CS101", "course_name": "Introduction to Computer Science", "instructor_name": "Dr. Alan Turing", "rating": 5, "comment": "Outstanding course!", "student_name": "Alice", "created_at": "2026-10-20T10:00:00"},
        {"id": 2, "course_id": 1, "course_code": "CS101", "course_name": "Introduction to Computer Science", "instructor_name": "Dr. Alan Turing", "rating": 4, "comment": "Very thorough.", "student_name": "Bob", "created_at": "2026-10-21T11:00:00"},
        {"id": 3, "course_id": 2, "course_code": "CS201", "course_name": "Data Structures and Algorithms", "instructor_name": "Dr. Ada Lovelace", "rating": 5, "comment": "Challenging but rewarding.", "student_name": "Charlie", "created_at": "2026-10-22T12:00:00"},
        {"id": 4, "course_id": 3, "course_code": "CS301", "course_name": "Database Management Systems", "instructor_name": "Dr. Edgar Codd", "rating": 2, "comment": "Needs better assignments.", "student_name": "Dave", "created_at": "2026-10-23T14:00:00"},
    ]
