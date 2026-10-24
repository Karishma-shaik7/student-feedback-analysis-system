"""
Tests for Flask routes and server-side form validation.
Verifies feedback validation, duplicate handling, and zero false-positive success toasts.
"""

from unittest.mock import patch
import pytest


def test_flask_app_starts(app):
    """Requirement 1: Verify the Flask application starts and loads configuration."""
    assert app is not None
    assert app.config["TESTING"] is True


def test_home_page_loads(client, sample_courses):
    """Requirement 2: Verify the home page loads successfully."""
    with patch("database.db.check_db_connection", return_value=(True, "Connected")), \
         patch("database.db.get_all_courses", return_value=sample_courses):
        response = client.get("/")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "Student Feedback Submission" in html
        assert "CS101" in html
        assert "Introduction to Computer Science" in html
        assert "Satisfaction Rating" in html


def test_feedback_form_rejects_missing_rating(client, sample_courses):
    """Requirement 3a: Verify form rejects submissions with missing rating."""
    with patch("database.db.get_course_by_id", return_value=sample_courses[0]):
        # Post with empty rating
        response = client.post("/submit-feedback", data={
            "course_id": "1",
            "rating": "",
            "comment": "Nice lecture",
        }, follow_redirects=True)

        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "Please provide a satisfaction rating between 1 and 5 stars" in html


def test_feedback_form_rejects_out_of_bounds_ratings(client, sample_courses):
    """Requirement 3b: Verify form rejects ratings < 1 or > 5 or invalid strings."""
    with patch("database.db.get_course_by_id", return_value=sample_courses[0]):
        # Rating 0 (too low)
        res_low = client.post("/submit-feedback", data={"course_id": "1", "rating": "0"}, follow_redirects=True)
        assert "Rating must be between 1 and 5 stars" in res_low.get_data(as_text=True)

        # Rating 6 (too high)
        res_high = client.post("/submit-feedback", data={"course_id": "1", "rating": "6"}, follow_redirects=True)
        assert "Rating must be between 1 and 5 stars" in res_high.get_data(as_text=True)

        # Rating non-numeric string
        res_text = client.post("/submit-feedback", data={"course_id": "1", "rating": "five"}, follow_redirects=True)
        assert "Invalid rating submitted" in res_text.get_data(as_text=True)


def test_unknown_courses_rejected(client):
    """Requirement 4: Verify unknown course IDs are rejected."""
    # Mock course not found
    with patch("database.db.get_course_by_id", return_value=None):
        response = client.post("/submit-feedback", data={
            "course_id": "9999",
            "rating": "5",
            "comment": "Unknown course review",
        }, follow_redirects=True)

        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "The selected course was not found in our catalog" in html


def test_valid_feedback_inserted_and_committed(client, sample_courses):
    """Requirement 5: Verify valid feedback is successfully inserted and triggers success message."""
    course = sample_courses[0]
    with patch("database.db.get_course_by_id", return_value=course), \
         patch("database.db.insert_feedback", return_value=(True, 101)) as mock_insert, \
         patch("database.db.get_all_courses", return_value=sample_courses), \
         patch("database.db.check_db_connection", return_value=(True, "Connected")):

        response = client.post("/submit-feedback", data={
            "course_id": "1",
            "rating": "5",
            "comment": "Superb professor and engaging lab assignments!",
            "student_name": "Test Student",
        }, follow_redirects=True)

        assert response.status_code == 200
        html = response.get_data(as_text=True)
        # Verify db insert was called with proper parameters
        mock_insert.assert_called_once_with(
            course_id=1,
            rating=5,
            comment="Superb professor and engaging lab assignments!",
            student_name="Test Student",
        )
        assert "recorded successfully" in html
        assert "CS101" in html


def test_failed_database_insert_never_shows_success(client, sample_courses):
    """Requirement 6: Verify a failed database insert does NOT show a success message."""
    course = sample_courses[0]
    # Simulate DB error during insertion
    with patch("database.db.get_course_by_id", return_value=course), \
         patch("database.db.insert_feedback", return_value=(False, "Connection timeout to MySQL host")), \
         patch("database.db.get_all_courses", return_value=sample_courses), \
         patch("database.db.check_db_connection", return_value=(True, "Connected")):

        response = client.post("/submit-feedback", data={
            "course_id": "1",
            "rating": "4",
            "comment": "Good course",
        }, follow_redirects=True)

        assert response.status_code == 200
        html = response.get_data(as_text=True)

        # STRICT ASSERTIONS: Must NEVER show success message
        assert "recorded successfully" not in html
        assert "Thank you" not in html
        # Must show danger / error alert
        assert "Unable to save feedback" in html
        assert "Connection timeout" in html


def test_not_found_404_page(client):
    """Verify custom 404 handler."""
    response = client.get("/nonexistent-endpoint-path")
    assert response.status_code == 404
    html = response.get_data(as_text=True)
    assert "Resource Not Found" in html
    assert "404" in html
