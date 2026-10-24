"""
Flask Web Application for Student Feedback Analysis System.

Provides student feedback intake and an executive administrative analytics dashboard.
Ensures secure parameterized queries, strict validation, and zero false-positive success states.
"""

import sys
import logging
from datetime import datetime
from typing import Optional

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    Response,
)

from config import get_config
import database.db as db_manager
import analytics.engine as analytics_engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("student_feedback.app")


def create_app(config_name: Optional[str] = None) -> Flask:
    """Application factory for Flask application."""
    app = Flask(__name__)
    config_cls = get_config(config_name)
    app.config.from_object(config_cls)

    # Register custom Jinja template filters
    @app.template_filter("format_datetime")
    def format_datetime(value, format_str="%b %d, %Y - %I:%M %p"):
        """Formats datetime objects or strings into clean, readable text."""
        if not value:
            return "N/A"
        if isinstance(value, str):
            try:
                dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
                return dt.strftime(format_str)
            except Exception:
                return value
        if hasattr(value, "strftime"):
            return value.strftime(format_str)
        return str(value)

    @app.template_filter("star_rating")
    def star_rating(rating_val):
        """Converts integer rating (1-5) to Unicode stars string."""
        try:
            r = int(rating_val)
            r = max(1, min(5, r))
            return "★" * r + "☆" * (5 - r)
        except (ValueError, TypeError):
            return "☆☆☆☆☆"

    # --------------------------------------------------------------------------
    # ROUTES
    # --------------------------------------------------------------------------

    @app.route("/", methods=["GET"])
    def index():
        """
        Student Feedback Submission Page.
        Fetches active courses from MySQL to populate the course dropdown.
        """
        is_healthy, db_message = db_manager.check_db_connection()
        courses = []
        if is_healthy:
            courses = db_manager.get_all_courses()
        else:
            logger.warning("Database unavailable on homepage load: %s", db_message)

        return render_template(
            "index.html",
            courses=courses,
            db_healthy=is_healthy,
            db_message=db_message,
        )

    @app.route("/submit-feedback", methods=["POST"])
    def submit_feedback():
        """
        Processes feedback form submission.
        Validates:
            - Selected course ID (must exist)
            - Rating (must be integer 1 to 5)
            - Optional sanitized comment
        
        Guarantees that a success message is NEVER displayed if the database insert fails.
        """
        raw_course_id = request.form.get("course_id")
        raw_rating = request.form.get("rating")
        raw_comment = request.form.get("comment", "")
        raw_student_name = request.form.get("student_name", "")

        # 1. Course validation
        if not raw_course_id:
            flash("Please select a course from the dropdown.", "danger")
            return redirect(url_for("index"))

        try:
            course_id = int(raw_course_id)
        except (ValueError, TypeError):
            flash("Invalid course selection. Please select a valid course.", "danger")
            return redirect(url_for("index"))

        # Verify course exists in database
        selected_course = db_manager.get_course_by_id(course_id)
        if not selected_course:
            flash("The selected course was not found in our catalog. Please try again.", "danger")
            return redirect(url_for("index"))

        # 2. Rating validation
        if not raw_rating:
            flash("Please provide a satisfaction rating between 1 and 5 stars.", "danger")
            return redirect(url_for("index"))

        try:
            rating = int(raw_rating)
            if rating < 1 or rating > 5:
                flash("Rating must be between 1 and 5 stars.", "danger")
                return redirect(url_for("index"))
        except (ValueError, TypeError):
            flash("Invalid rating submitted. Please click 1 to 5 stars.", "danger")
            return redirect(url_for("index"))

        # 3. Database Insertion with Transaction
        success, result_or_err = db_manager.insert_feedback(
            course_id=course_id,
            rating=rating,
            comment=raw_comment,
            student_name=raw_student_name,
        )

        if success:
            course_label = f"{selected_course['course_code']} - {selected_course['course_name']}"
            flash(
                f"Thank you! Your feedback for {course_label} ({rating} ★) was recorded successfully.",
                "success",
            )
            return redirect(url_for("index", submitted="1"))
        else:
            # Under NO circumstance display a success message on failure
            logger.error("Failed feedback insert for course ID %s: %s", course_id, result_or_err)
            flash(
                f"Unable to save feedback: {result_or_err}. Please ensure your database is running and try again.",
                "danger",
            )
            return redirect(url_for("index"))

    @app.route("/dashboard", methods=["GET"])
    def dashboard():
        """
        Executive Analytics Dashboard.
        Computes summary metrics using Pandas and renders Matplotlib charts.
        Handles zero-records gracefully without crashing.
        """
        is_healthy, db_message = db_manager.check_db_connection()
        all_courses = []
        feedback_records = []

        if is_healthy:
            all_courses = db_manager.get_all_courses()
            feedback_records = db_manager.get_all_feedback_joined()
        else:
            logger.warning("Database unavailable on dashboard load: %s", db_message)

        # Compute Pandas metrics
        metrics = analytics_engine.compute_feedback_metrics(feedback_records, all_courses)

        # Generate Matplotlib visualizations
        charts = analytics_engine.generate_all_dashboard_charts(metrics)

        return render_template(
            "dashboard.html",
            metrics=metrics,
            charts=charts,
            db_healthy=is_healthy,
            db_message=db_message,
        )

    @app.route("/api/health", methods=["GET"])
    def api_health():
        """Diagnostic health check endpoint (does not leak sensitive secrets)."""
        is_healthy, message = db_manager.check_db_connection()
        safe_info = config_cls.get_safe_info()
        return jsonify({
            "status": "healthy" if is_healthy else "degraded",
            "database_connected": is_healthy,
            "database_message": message,
            "configuration": safe_info,
        }), 200 if is_healthy else 503

    # --------------------------------------------------------------------------
    # ERROR HANDLERS
    # --------------------------------------------------------------------------

    @app.errorhandler(404)
    def handle_not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def handle_server_error(e):
        logger.error("Internal Server Error: %s", e)
        return render_template("500.html"), 500

    return app


# Application entry point
app = create_app()

if __name__ == "__main__":
    config = get_config()
    print(f"\n🚀 Student Feedback Analysis System is starting...")
    print(f"👉 Student Feedback Form: http://127.0.0.1:5000/")
    print(f"👉 Analytics Dashboard:  http://127.0.0.1:5000/dashboard")
    print(f"👉 Health Check API:     http://127.0.0.1:5000/api/health\n")
    app.run(host="127.0.0.1", port=5000, debug=config.DEBUG)
