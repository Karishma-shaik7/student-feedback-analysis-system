"""
Tests for UI/UX responsiveness and accessibility requirements.
Requirement 10: The UI works at mobile and desktop sizes.
"""

from pathlib import Path
from unittest.mock import patch
import pytest


def test_meta_viewport_present_in_templates(client):
    """Verify viewport meta tag is present for responsive scaling on mobile/tablet."""
    with patch("database.db.check_db_connection", return_value=(True, "Connected")), \
         patch("database.db.get_all_courses", return_value=[]):
        res = client.get("/")
        html = res.get_data(as_text=True)
        assert '<meta name="viewport" content="width=device-width, initial-scale=1.0">' in html


def test_responsive_sidebar_and_mobile_toggle(client):
    """Verify mobile menu toggle button and sidebar classes exist."""
    with patch("database.db.check_db_connection", return_value=(True, "Connected")), \
         patch("database.db.get_all_courses", return_value=[]):
        res = client.get("/")
        html = res.get_data(as_text=True)
        assert 'id="mobile-toggle"' in html
        assert 'aria-label="Toggle Navigation Menu"' in html
        assert 'class="app-sidebar"' in html


def test_css_contains_mobile_and_desktop_media_queries():
    """Verify style.css contains standard responsive breakpoints."""
    css_path = Path(__file__).resolve().parent.parent / "static" / "css" / "style.css"
    assert css_path.exists(), "style.css must exist"
    css_content = css_path.read_text(encoding="utf-8")

    assert "@media (max-width: 768px)" in css_content
    assert "@media (max-width: 1024px)" in css_content
    assert ".table-responsive" in css_content
    assert "--sidebar-width" in css_content


def test_dashboard_table_has_responsive_wrapper(client, sample_feedback, sample_courses):
    """Verify table is wrapped inside .table-responsive for mobile horizontal scroll."""
    with patch("database.db.check_db_connection", return_value=(True, "Connected")), \
         patch("database.db.get_all_courses", return_value=sample_courses), \
         patch("database.db.get_all_feedback_joined", return_value=sample_feedback):
        res = client.get("/dashboard")
        html = res.get_data(as_text=True)
        assert 'class="table-responsive"' in html
        assert 'class="data-table"' in html
