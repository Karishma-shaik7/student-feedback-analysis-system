"""
Analytics and Visualization Engine for Student Feedback Analysis System.

Uses Pandas for statistical calculations and aggregation, and Matplotlib (Agg backend)
to render high-contrast, publication-quality dark-themed charts.
Handles empty datasets gracefully without crashing.
"""

import base64
import io
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")  # Headless backend safe for web servers & background threads
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config import get_config

logger = logging.getLogger("student_feedback.analytics")

# Chart Design Constants matching our Dark Navy / Purple UI Theme
CHART_BG_COLOR = "#111827"       # Tailwind gray-900 / dark card surface
CHART_AXIS_BG = "#1f2937"        # Tailwind gray-800
CHART_TEXT_COLOR = "#f3f4f6"     # Off-white
CHART_MUTED_TEXT = "#9ca3af"     # Light slate
CHART_GRID_COLOR = "#374151"     # Dark slate subtle border
VIOLET_ACCENT = "#8b5cf6"        # Primary accent
CYAN_ACCENT = "#06b6d4"          # Cyan accent
BLUE_ACCENT = "#3b82f6"          # Blue accent
EMERALD_ACCENT = "#10b981"       # Success green
AMBER_ACCENT = "#f59e0b"         # Amber
ROSE_ACCENT = "#f43f5e"          # Rose red


def compute_feedback_metrics(
    feedback_records: List[Dict[str, Any]], 
    all_courses: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Analyzes student feedback records using Pandas.
    
    Computes:
        - Total feedback responses
        - Overall average rating
        - Total active courses count
        - Highest-rated course (code, name, and score)
        - Course-level aggregations (count, average rating)
        - Star distribution breakdown (1 to 5 stars)
    
    Returns a structured dictionary with all KPIs and safe fallbacks for empty datasets.
    """
    total_courses_count = len(all_courses)

    # Empty state handling
    if not feedback_records:
        return {
            "has_data": False,
            "total_responses": 0,
            "overall_avg_rating": 0.0,
            "overall_avg_display": "0.00",
            "total_courses": total_courses_count,
            "highest_rated_course": None,
            "course_stats": [],
            "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
            "recent_feedback": [],
        }

    # Convert to Pandas DataFrame
    df = pd.DataFrame(feedback_records)

    # Ensure rating is numeric
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df = df.dropna(subset=["rating"])

    if df.empty:
        return {
            "has_data": False,
            "total_responses": 0,
            "overall_avg_rating": 0.0,
            "overall_avg_display": "0.00",
            "total_courses": total_courses_count,
            "highest_rated_course": None,
            "course_stats": [],
            "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
            "recent_feedback": [],
        }

    total_responses = int(len(df))
    overall_avg = float(df["rating"].mean())

    # Rating distribution across 1 to 5 stars
    dist_counts = df["rating"].value_counts().to_dict()
    rating_distribution = {star: int(dist_counts.get(star, 0)) for star in range(1, 6)}

    # Aggregation by Course
    # Group by course_id, course_code, course_name
    grouped = df.groupby(["course_id", "course_code", "course_name"]).agg(
        response_count=("rating", "count"),
        avg_rating=("rating", "mean"),
    ).reset_index()

    grouped["avg_rating"] = grouped["avg_rating"].round(2)
    course_stats = grouped.to_dict(orient="records")

    # Find highest rated course (sorting by avg_rating DESC, then response_count DESC)
    highest_rated = None
    if not grouped.empty:
        top_row = grouped.sort_values(by=["avg_rating", "response_count"], ascending=[False, False]).iloc[0]
        highest_rated = {
            "course_id": int(top_row["course_id"]),
            "course_code": str(top_row["course_code"]),
            "course_name": str(top_row["course_name"]),
            "avg_rating": float(top_row["avg_rating"]),
            "avg_display": f"{top_row['avg_rating']:.2f}",
            "response_count": int(top_row["response_count"]),
        }

    return {
        "has_data": True,
        "total_responses": total_responses,
        "overall_avg_rating": round(overall_avg, 2),
        "overall_avg_display": f"{overall_avg:.2f}",
        "total_courses": total_courses_count,
        "highest_rated_course": highest_rated,
        "course_stats": course_stats,
        "rating_distribution": rating_distribution,
        "recent_feedback": feedback_records[:10],  # top 10 most recent
    }


def _setup_figure_style(fig, ax, title: str):
    """Applies unified dark theme styling to a Matplotlib figure and axis."""
    fig.patch.set_facecolor(CHART_BG_COLOR)
    ax.set_facecolor(CHART_AXIS_BG)
    ax.set_title(title, fontsize=13, fontweight="bold", color=CHART_TEXT_COLOR, pad=15)
    ax.tick_params(colors=CHART_MUTED_TEXT, labelsize=10)
    ax.spines["bottom"].set_color(CHART_GRID_COLOR)
    ax.spines["left"].set_color(CHART_GRID_COLOR)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", linestyle="--", alpha=0.3, color=CHART_GRID_COLOR)


def _figure_to_base64_and_file(fig, filename: str) -> str:
    """
    Saves figure to disk (in static/images/charts) and returns base64 data URI string.
    """
    config_cls = get_config()
    chart_dir = config_cls.CHART_OUTPUT_DIR
    chart_dir.mkdir(parents=True, exist_ok=True)
    file_path = chart_dir / filename

    # Save to disk
    fig.savefig(file_path, format="png", dpi=140, bbox_inches="tight", facecolor=fig.get_facecolor(), edgecolor="none")

    # Save to in-memory buffer for base64 return
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=140, bbox_inches="tight", facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()
    return f"data:image/png;base64,{img_b64}"


def generate_avg_rating_by_course_chart(course_stats: List[Dict[str, Any]]) -> Optional[str]:
    """
    Visualizes average rating by course using a horizontal bar chart with exact values labeled.
    """
    if not course_stats:
        return None

    # Sort courses by average rating descending
    sorted_stats = sorted(course_stats, key=lambda x: x["avg_rating"], reverse=True)
    labels = [f"{c['course_code']} - {c['course_name'][:20]}" for c in sorted_stats]
    scores = [c["avg_rating"] for c in sorted_stats]

    fig, ax = plt.subplots(figsize=(7, max(3.5, len(labels) * 0.6)))
    _setup_figure_style(fig, ax, "Average Course Satisfaction (1 - 5 ★)")

    y_pos = np.arange(len(labels))
    bars = ax.barh(y_pos, scores, color=VIOLET_ACCENT, height=0.55, edgecolor="#a78bfa", linewidth=1.2)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, color=CHART_TEXT_COLOR, fontsize=10)
    ax.set_xlim(0, 5.5)
    ax.set_xlabel("Average Rating (Out of 5.0)", color=CHART_MUTED_TEXT, fontsize=10, labelpad=8)
    ax.invert_yaxis()  # Highest rating on top

    # Add numeric value badges to the right of each bar
    for bar, score in zip(bars, scores):
        width = bar.get_width()
        ax.text(
            width + 0.1,
            bar.get_y() + bar.get_height() / 2,
            f"{score:.2f} ★",
            va="center",
            ha="left",
            color="#fbbf24",  # Amber gold
            fontweight="bold",
            fontsize=10,
        )

    plt.tight_layout()
    return _figure_to_base64_and_file(fig, "avg_rating_by_course.png")


def generate_rating_distribution_chart(rating_distribution: Dict[int, int]) -> Optional[str]:
    """
    Visualizes the count of 1-star through 5-star ratings with distinct color-coded bars.
    """
    if not rating_distribution or sum(rating_distribution.values()) == 0:
        return None

    stars = [1, 2, 3, 4, 5]
    counts = [rating_distribution.get(s, 0) for s in stars]
    labels = ["1 Star", "2 Stars", "3 Stars", "4 Stars", "5 Stars"]
    colors = [ROSE_ACCENT, "#fb923c", AMBER_ACCENT, BLUE_ACCENT, EMERALD_ACCENT]

    fig, ax = plt.subplots(figsize=(6.5, 4))
    fig.patch.set_facecolor(CHART_BG_COLOR)
    ax.set_facecolor(CHART_AXIS_BG)
    ax.set_title("Rating Distribution (All Feedback)", fontsize=13, fontweight="bold", color=CHART_TEXT_COLOR, pad=15)
    ax.tick_params(colors=CHART_MUTED_TEXT, labelsize=10)
    ax.spines["bottom"].set_color(CHART_GRID_COLOR)
    ax.spines["left"].set_color(CHART_GRID_COLOR)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.3, color=CHART_GRID_COLOR)

    x_pos = np.arange(len(stars))
    bars = ax.bar(x_pos, counts, color=colors, width=0.55, edgecolor="#ffffff", linewidth=0.5)

    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, color=CHART_TEXT_COLOR, fontsize=10)
    ax.set_ylabel("Number of Responses", color=CHART_MUTED_TEXT, fontsize=10, labelpad=8)
    ax.set_ylim(0, max(counts) * 1.25 if max(counts) > 0 else 5)

    # Label counts on top of bars
    total = sum(counts)
    for bar, count in zip(bars, counts):
        height = bar.get_height()
        pct = (count / total * 100) if total > 0 else 0
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + (max(counts) * 0.03 if max(counts) > 0 else 0.2),
            f"{count} ({pct:.0f}%)",
            ha="center",
            va="bottom",
            color=CHART_TEXT_COLOR,
            fontsize=9,
            fontweight="bold",
        )

    plt.tight_layout()
    return _figure_to_base64_and_file(fig, "rating_distribution.png")


def generate_responses_per_course_chart(course_stats: List[Dict[str, Any]]) -> Optional[str]:
    """
    Visualizes student feedback response volume per course.
    """
    if not course_stats:
        return None

    # Sort courses by response count descending
    sorted_stats = sorted(course_stats, key=lambda x: x["response_count"], reverse=True)
    labels = [c["course_code"] for c in sorted_stats]
    counts = [c["response_count"] for c in sorted_stats]

    fig, ax = plt.subplots(figsize=(6.5, 4))
    fig.patch.set_facecolor(CHART_BG_COLOR)
    ax.set_facecolor(CHART_AXIS_BG)
    ax.set_title("Response Volume by Course Code", fontsize=13, fontweight="bold", color=CHART_TEXT_COLOR, pad=15)
    ax.tick_params(colors=CHART_MUTED_TEXT, labelsize=10)
    ax.spines["bottom"].set_color(CHART_GRID_COLOR)
    ax.spines["left"].set_color(CHART_GRID_COLOR)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.3, color=CHART_GRID_COLOR)

    x_pos = np.arange(len(labels))
    bars = ax.bar(x_pos, counts, color=CYAN_ACCENT, width=0.5, edgecolor="#67e8f9", linewidth=1.0)

    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, color=CHART_TEXT_COLOR, fontsize=10, rotation=25 if len(labels) > 5 else 0)
    ax.set_ylabel("Total Responses", color=CHART_MUTED_TEXT, fontsize=10, labelpad=8)
    ax.set_ylim(0, max(counts) * 1.25 if max(counts) > 0 else 5)

    for bar, count in zip(bars, counts):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + (max(counts) * 0.03 if max(counts) > 0 else 0.2),
            f"{count}",
            ha="center",
            va="bottom",
            color=CHART_TEXT_COLOR,
            fontsize=9,
            fontweight="bold",
        )

    plt.tight_layout()
    return _figure_to_base64_and_file(fig, "responses_per_course.png")


def generate_all_dashboard_charts(
    metrics: Dict[str, Any]
) -> Dict[str, Optional[str]]:
    """
    Generates all three dashboard charts and returns base64 image strings.
    Handles empty cases by returning None for each chart.
    """
    if not metrics.get("has_data", False):
        return {
            "avg_rating_chart": None,
            "rating_dist_chart": None,
            "responses_chart": None,
        }

    course_stats = metrics.get("course_stats", [])
    rating_distribution = metrics.get("rating_distribution", {})

    return {
        "avg_rating_chart": generate_avg_rating_by_course_chart(course_stats),
        "rating_dist_chart": generate_rating_distribution_chart(rating_distribution),
        "responses_chart": generate_responses_per_course_chart(course_stats),
    }
