"""
Tests for Pandas analytics aggregation and Matplotlib chart generation.
Verifies math accuracy, empty state handling, and headless chart creation.
"""

from unittest.mock import patch
import pytest
import analytics.engine as engine


def test_dashboard_calculates_correct_totals_and_averages(sample_feedback, sample_courses):
    """
    Requirement 7: Verify totals and averages calculated by Pandas.
    sample_feedback ratings: CS101: 5, 4 (avg = 4.5); CS201: 5 (avg = 5.0); CS301: 2 (avg = 2.0).
    Overall sum = 5 + 4 + 5 + 2 = 16. Count = 4. Mean = 4.0.
    """
    metrics = engine.compute_feedback_metrics(sample_feedback, sample_courses)

    assert metrics["has_data"] is True
    assert metrics["total_responses"] == 4
    assert metrics["overall_avg_rating"] == 4.0
    assert metrics["overall_avg_display"] == "4.00"
    assert metrics["total_courses"] == len(sample_courses)

    # Verify highest rated course logic (CS201 has avg 5.0)
    top_course = metrics["highest_rated_course"]
    assert top_course is not None
    assert top_course["course_code"] == "CS201"
    assert top_course["avg_rating"] == 5.0

    # Verify star distribution counts
    # Ratings: 2 (count 1), 4 (count 1), 5 (count 2)
    dist = metrics["rating_distribution"]
    assert dist[1] == 0
    assert dist[2] == 1
    assert dist[3] == 0
    assert dist[4] == 1
    assert dist[5] == 2


def test_empty_feedback_data_does_not_crash_dashboard(sample_courses):
    """
    Requirement 8: Verify empty feedback data does not crash the dashboard
    and returns sensible empty defaults.
    """
    empty_records = []
    metrics = engine.compute_feedback_metrics(empty_records, sample_courses)

    assert metrics["has_data"] is False
    assert metrics["total_responses"] == 0
    assert metrics["overall_avg_rating"] == 0.0
    assert metrics["overall_avg_display"] == "0.00"
    assert metrics["total_courses"] == len(sample_courses)
    assert metrics["highest_rated_course"] is None
    assert metrics["course_stats"] == []

    # Chart generation for empty metrics must return None without raising exceptions
    charts = engine.generate_all_dashboard_charts(metrics)
    assert charts["avg_rating_chart"] is None
    assert charts["rating_dist_chart"] is None
    assert charts["responses_chart"] is None


def test_dashboard_charts_are_generated_correctly(sample_feedback, sample_courses):
    """
    Requirement 9: Verify dashboard charts are generated with valid base64 image URIs.
    """
    metrics = engine.compute_feedback_metrics(sample_feedback, sample_courses)
    charts = engine.generate_all_dashboard_charts(metrics)

    # Check that all 3 charts were rendered
    assert charts["avg_rating_chart"] is not None
    assert charts["rating_dist_chart"] is not None
    assert charts["responses_chart"] is not None

    # Verify base64 data URI format
    for chart_key in ["avg_rating_chart", "rating_dist_chart", "responses_chart"]:
        uri = charts[chart_key]
        assert uri.startswith("data:image/png;base64,")
        assert len(uri) > 100  # Non-empty base64 image data


def test_dashboard_endpoint_with_data(client, sample_feedback, sample_courses):
    """Verify GET /dashboard renders all KPI cards and charts when data exists."""
    with patch("database.db.check_db_connection", return_value=(True, "Connected")), \
         patch("database.db.get_all_courses", return_value=sample_courses), \
         patch("database.db.get_all_feedback_joined", return_value=sample_feedback):

        response = client.get("/dashboard")
        assert response.status_code == 200
        html = response.get_data(as_text=True)

        # Check KPI values
        assert "Total Responses" in html
        assert "Average Satisfaction" in html
        assert "4.00" in html
        assert "CS201" in html

        # Check chart images embedded
        assert 'src="data:image/png;base64,' in html

        # Check recent feedback table records
        assert "Alice" in html
        assert "Outstanding course!" in html
        assert "Charlie" in html


def test_dashboard_endpoint_empty_state(client, sample_courses):
    """Verify GET /dashboard renders the empty state when no feedback is recorded."""
    with patch("database.db.check_db_connection", return_value=(True, "Connected")), \
         patch("database.db.get_all_courses", return_value=sample_courses), \
         patch("database.db.get_all_feedback_joined", return_value=[]):

        response = client.get("/dashboard")
        assert response.status_code == 200
        html = response.get_data(as_text=True)

        # Must display empty state container
        assert "No Feedback Submissions Yet" in html
        assert "Submit First Evaluation" in html
        assert "0" in html  # Total responses = 0
