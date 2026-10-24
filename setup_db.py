"""
Convenience Database Setup Script for Student Feedback Analysis System.

Allows beginners to quickly initialize or verify the MySQL database schema and seed courses
from Windows PowerShell by running:
    python setup_db.py

Reads connection credentials securely from .env.
"""

import sys

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from config import get_config
import database.db as db_manager


def main():
    print("=" * 70)
    print("[EduPulse] Student Feedback Analysis System - Database Initializer")
    print("=" * 70)

    config_cls = get_config()
    safe_info = config_cls.get_safe_info()

    print(f"Target Host:     {safe_info['mysql_host']}:{safe_info['mysql_port']}")
    print(f"Target Database: {safe_info['mysql_database']}")
    print(f"Target User:     {safe_info['mysql_user']}")
    print(f"Password Set:    {'Yes' if safe_info['mysql_password_configured'] else 'No (Empty)'}")
    print("-" * 70)

    print("Attempting to connect and initialize database schema...")
    success, message = db_manager.init_db()

    if success:
        print("\n[SUCCESS] " + message)
        healthy, health_msg = db_manager.check_db_connection()
        if healthy:
            courses = db_manager.get_all_courses()
            print(f"Catalog verified: {len(courses)} active courses cataloged:")
            for c in courses:
                print(f"  * {c['course_code']}: {c['course_name']} ({c['instructor_name']})")
        print("\nYou can now launch the application using: python app.py")
        sys.exit(0)
    else:
        print("\n[FAILED] " + message)
        print("\nTroubleshooting Guidance:")
        print("1. Ensure MySQL service is running: Get-Service MySQL80")
        print("2. Ensure your password in '.env' matches your MySQL root password.")
        print("3. If you haven't created a .env file yet, run: Copy-Item .env.example .env")
        sys.exit(1)


if __name__ == "__main__":
    main()
