"""
Centralized Configuration Module for Student Feedback Analysis System.

Handles environment variable loading, validation, and database connection settings.
Never hardcodes sensitive credentials into source code.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file if it exists
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)

logger = logging.getLogger("student_feedback.config")


class BaseConfig:
    """Base configuration shared across environments."""
    ENV = os.getenv("FLASK_ENV", "development").lower()
    DEBUG = os.getenv("FLASK_DEBUG", "0").lower() in ("1", "true", "yes")
    TESTING = False

    # Secret key for sessions, flash messages, and CSRF protection
    _DEFAULT_DEV_SECRET = "dev-insecure-key-only-for-local-demo-do-not-use-in-production"
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", _DEFAULT_DEV_SECRET)

    # MySQL Database Connection Settings
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    try:
        MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
    except ValueError:
        MYSQL_PORT = 3306

    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "student_feedback_db")

    # Matplotlib Chart Output Directory
    CHART_OUTPUT_DIR = BASE_DIR / "static" / "images" / "charts"

    @classmethod
    def get_mysql_config(cls) -> dict:
        """Returns the dictionary needed for mysql.connector.connect()."""
        return {
            "host": cls.MYSQL_HOST,
            "port": cls.MYSQL_PORT,
            "user": cls.MYSQL_USER,
            "password": cls.MYSQL_PASSWORD,
            "database": cls.MYSQL_DATABASE,
            "charset": "utf8mb4",
            "autocommit": False,  # Explicit transaction commits & rollbacks
        }

    @classmethod
    def get_safe_info(cls) -> dict:
        """Returns non-sensitive configuration summary for health checks and diagnostics."""
        return {
            "environment": cls.ENV,
            "mysql_host": cls.MYSQL_HOST,
            "mysql_port": cls.MYSQL_PORT,
            "mysql_user": cls.MYSQL_USER,
            "mysql_database": cls.MYSQL_DATABASE,
            "mysql_password_configured": bool(cls.MYSQL_PASSWORD),
            "secret_key_configured": cls.SECRET_KEY != cls._DEFAULT_DEV_SECRET,
        }


class DevelopmentConfig(BaseConfig):
    """Development environment settings."""
    DEBUG = True


class TestingConfig(BaseConfig):
    """Testing environment settings."""
    TESTING = True
    DEBUG = True
    MYSQL_DATABASE = os.getenv("MYSQL_TEST_DATABASE", "student_feedback_test_db")
    SECRET_KEY = "test-secret-key-for-automated-tests"


class ProductionConfig(BaseConfig):
    """Production environment settings with strict safety checks."""
    DEBUG = False
    TESTING = False

    @classmethod
    def validate(cls):
        """Enforce production security rules."""
        if cls.SECRET_KEY == cls._DEFAULT_DEV_SECRET or not cls.SECRET_KEY:
            raise ValueError(
                "CRITICAL: FLASK_SECRET_KEY must be set to a secure, unique string in production!"
            )
        if not cls.MYSQL_PASSWORD:
            logger.warning("Production MySQL password is empty. Ensure your database is properly secured.")


# Configuration mapping
CONFIG_MAP = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(env_name: str = None) -> type[BaseConfig]:
    """Retrieve the configuration class based on environment."""
    if env_name is None:
        env_name = os.getenv("FLASK_ENV", "development").lower()
    config_cls = CONFIG_MAP.get(env_name, DevelopmentConfig)
    if env_name == "production":
        config_cls.validate()
    return config_cls
