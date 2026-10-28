"""
Database Management Module for Student Feedback Analysis System.

Provides robust, parameterized connection handling, transaction management,
connection testing, schema initialization, and CRUD operations using mysql-connector-python.
All credentials are loaded securely from config.py / environment variables.
"""

import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Optional, Tuple, List, Dict
import mysql.connector
from mysql.connector import Error, errorcode

from config import get_config

logger = logging.getLogger("student_feedback.db")


def get_db_connection(database_override: Optional[str] = None, use_database: bool = True):
    """
    Creates and returns a new MySQL database connection using parameterized config.

    All connection parameters — including SSL settings — are taken directly from
    config.get_mysql_config(), so credentials and certificate paths are never
    hardcoded here.

    Args:
        database_override: Optional database name to override config.
        use_database: If False, connects to MySQL server without selecting a database
                      (useful for CREATE DATABASE commands).
    """
    config_cls = get_config()
    db_config = config_cls.get_mysql_config()

    # Start from the full config dict returned by get_mysql_config().
    # This already contains all SSL keys when they are configured.
    connection_params = dict(db_config)
    connection_params["connect_timeout"] = 10

    if use_database:
        connection_params["database"] = database_override or db_config.get("database")
    else:
        # Remove the database key so we can connect at server level
        connection_params.pop("database", None)

    try:
        conn = mysql.connector.connect(**connection_params)
        return conn
    except Error as err:
        # Diagnostic logging for developers without exposing passwords
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            logger.error("Database connection error: Invalid username or password for host '%s'", db_config['host'])
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            logger.error("Database connection error: Database '%s' does not exist", db_config.get('database', ''))
        else:
            logger.error("Database connection error [%d]: %s", err.errno, err.msg)
        raise


@contextmanager
def get_db_cursor(commit: bool = False, dictionary: bool = True):
    """
    Context manager that yields a cursor and connection with automated transaction handling.
    
    If commit=True, commits on clean block completion.
    Rolls back automatically upon any encountered exception.
    Always closes both cursor and connection cleanly.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=dictionary)
        yield cursor, conn
        if commit:
            conn.commit()
    except Exception as exc:
        if conn and conn.is_connected():
            try:
                conn.rollback()
                logger.warning("Database transaction rolled back due to error: %s", exc)
            except Error as rollback_err:
                logger.error("Failed to rollback transaction: %s", rollback_err)
        raise
    finally:
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass
        if conn is not None and conn.is_connected():
            try:
                conn.close()
            except Exception:
                pass


def check_db_connection() -> Tuple[bool, str]:
    """
    Verifies that the database server is reachable and credentials are valid.
    
    Returns:
        Tuple[bool, str]: (is_healthy, status_message)
    """
    try:
        with get_db_cursor(commit=False) as (cursor, _):
            cursor.execute("SELECT 1 AS health_check;")
            row = cursor.fetchone()
            if row and (row.get("health_check") == 1 or row[0] == 1):
                return True, "Database connection active and responsive."
            return False, "Unexpected response from database health query."
    except Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            return False, "Access denied: Please verify MYSQL_USER and MYSQL_PASSWORD in your .env file."
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            return False, "Database not found: Run schema.sql or initialize via database setup."
        elif err.errno == 2003:  # Can't connect to MySQL server
            return False, "Cannot reach MySQL server: Please ensure MySQL80 service is running."
        return False, f"Database connection issue: {err.msg}"
    except Exception as exc:
        return False, f"Database error: {str(exc)}"


def init_db(schema_file_path: Optional[str] = None, database_name: Optional[str] = None) -> Tuple[bool, str]:
    """
    Safely creates the `courses` and `feedback` tables and inserts the sample
    courses in the database specified by `database_name` or `MYSQL_DATABASE` (e.g. defaultdb).
    
    Guarantees:
        - Creates tables in the database selected by MYSQL_DATABASE.
        - Never drops tables or deletes existing feedback data.
        - Uses duplicate-safe inserts (INSERT IGNORE) for sample courses.
        - Preserves all SSL/TLS and connection configurations.
        - Handles local MySQL environments by creating database if allowed/needed.
    """
    config_cls = get_config()
    target_db = database_name or config_cls.MYSQL_DATABASE

    # For local dev environments, try to ensure the target database exists if possible.
    # On managed cloud hosts (like Aiven), databases are pre-created (e.g. defaultdb)
    # and server-level commands without a database may be restricted or unsupported.
    try:
        server_conn = get_db_connection(use_database=False)
        try:
            with server_conn.cursor() as s_cur:
                s_cur.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{target_db}` "
                    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
                )
            server_conn.commit()
        finally:
            server_conn.close()
    except Exception as db_create_err:
        logger.debug("Server-level database check skipped or restricted: %s", db_create_err)

    if schema_file_path is None:
        schema_file_path = Path(__file__).resolve().parent / "schema.sql"
    else:
        schema_file_path = Path(schema_file_path)

    if not schema_file_path.exists():
        return False, f"Schema file not found at {schema_file_path}"

    with open(schema_file_path, "r", encoding="utf-8") as f:
        sql_script = f.read()

    # Split SQL commands by semicolon, ignoring empty statements and comments
    statements = []
    for raw_stmt in sql_script.split(";"):
        stmt = raw_stmt.strip()
        # Strictly filter out any destructive or database-switching statements for safety
        upper_stmt = stmt.upper()
        if upper_stmt.startswith("DROP ") or upper_stmt.startswith("USE ") or upper_stmt.startswith("CREATE DATABASE "):
            continue
        if stmt:
            statements.append(stmt)

    conn = None
    cursor = None
    try:
        # Connect directly to the target database (e.g. defaultdb or student_feedback_db)
        conn = get_db_connection(database_override=target_db, use_database=True)
        cursor = conn.cursor()
        for statement in statements:
            # Skip pure comment blocks
            lines = [line.strip() for line in statement.splitlines() if line.strip() and not line.strip().startswith("--")]
            if lines:
                cursor.execute(statement)
        conn.commit()
        return True, f"Database '{target_db}' schema initialized safely and seed courses verified."
    except Error as err:
        if conn and conn.is_connected():
            conn.rollback()
        logger.error("Error executing database schema on '%s': %s", target_db, err)
        return False, f"Failed to initialize schema on '{target_db}': {err.msg}"
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()


def get_all_courses() -> List[Dict[str, Any]]:
    """
    Fetches all active courses sorted by course code.
    Uses parameterized query. If tables do not exist yet, auto-initializes once.
    """
    query = """
        SELECT id, course_code, course_name, instructor_name, department, created_at
        FROM courses
        ORDER BY course_code ASC;
    """
    try:
        with get_db_cursor(commit=False, dictionary=True) as (cursor, _):
            cursor.execute(query)
            return cursor.fetchall() or []
    except Error as err:
        if err.errno == errorcode.ER_NO_SUCH_TABLE:
            logger.info("Table 'courses' does not exist yet. Running safe initialization...")
            init_ok, _ = init_db()
            if init_ok:
                try:
                    with get_db_cursor(commit=False, dictionary=True) as (cursor, _):
                        cursor.execute(query)
                        return cursor.fetchall() or []
                except Exception as retry_err:
                    logger.error("Failed to fetch courses after initialization: %s", retry_err)
        logger.error("Failed to fetch courses: %s", err)
        return []
    except Exception as err:
        logger.error("Failed to fetch courses: %s", err)
        return []


def get_course_by_id(course_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetches a single course by its primary key ID.
    Uses parameterized query to prevent injection.
    """
    query = """
        SELECT id, course_code, course_name, instructor_name, department
        FROM courses
        WHERE id = %s;
    """
    try:
        with get_db_cursor(commit=False, dictionary=True) as (cursor, _):
            cursor.execute(query, (course_id,))
            return cursor.fetchone()
    except Exception as err:
        logger.error("Failed to fetch course ID %s: %s", course_id, err)
        return None


def insert_feedback(course_id: int, rating: int, comment: Optional[str] = None, student_name: Optional[str] = None) -> Tuple[bool, Any]:
    """
    Inserts a feedback record into the feedback table using explicit transactions.
    
    Validations:
        - Course must exist in courses table.
        - Rating must be integer between 1 and 5.
        - Comment sanitized and length bounded.
    
    Returns:
        Tuple[bool, Any]: (True, new_id) if successful, (False, error_message) on failure.
    """
    # Server-side validation
    try:
        rating_int = int(rating)
        if rating_int < 1 or rating_int > 5:
            return False, "Rating must be an integer between 1 and 5."
    except (ValueError, TypeError):
        return False, "Invalid rating value. Must be an integer between 1 and 5."

    try:
        course_id_int = int(course_id)
    except (ValueError, TypeError):
        return False, "Invalid course selection."

    # Verify course existence
    course = get_course_by_id(course_id_int)
    if not course:
        return False, f"Course with ID {course_id_int} does not exist."

    # Clean comment & student_name
    clean_comment = comment.strip() if comment and isinstance(comment, str) else None
    if clean_comment and len(clean_comment) > 2000:
        clean_comment = clean_comment[:2000]

    clean_name = student_name.strip() if student_name and isinstance(student_name, str) else None
    if clean_name and len(clean_name) > 100:
        clean_name = clean_name[:100]

    insert_sql = """
        INSERT INTO feedback (course_id, rating, comment, student_name)
        VALUES (%s, %s, %s, %s);
    """

    try:
        with get_db_cursor(commit=True, dictionary=True) as (cursor, conn):
            cursor.execute(insert_sql, (course_id_int, rating_int, clean_comment, clean_name))
            new_id = cursor.lastrowid
            logger.info("Successfully inserted feedback ID %s for course ID %s with rating %s", new_id, course_id_int, rating_int)
            return True, new_id
    except Error as db_err:
        logger.error("Database insert failed for course %s: %s", course_id_int, db_err)
        return False, f"Database error while saving feedback: {db_err.msg}"
    except Exception as exc:
        logger.error("Unexpected error saving feedback: %s", exc)
        return False, "A system error occurred while recording your feedback. Please try again."


def get_all_feedback_joined(limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Fetches feedback records joined with course details for analysis and display.
    """
    base_sql = """
        SELECT 
            f.id,
            f.course_id,
            c.course_code,
            c.course_name,
            c.instructor_name,
            c.department,
            f.rating,
            f.comment,
            f.student_name,
            f.created_at
        FROM feedback f
        JOIN courses c ON f.course_id = c.id
        ORDER BY f.created_at DESC
    """
    if limit and isinstance(limit, int) and limit > 0:
        base_sql += f" LIMIT {limit}"

    try:
        with get_db_cursor(commit=False, dictionary=True) as (cursor, _):
            cursor.execute(base_sql)
            return cursor.fetchall() or []
    except Error as err:
        if err.errno == errorcode.ER_NO_SUCH_TABLE:
            logger.info("Feedback or courses table does not exist yet. Running safe initialization...")
            init_ok, _ = init_db()
            if init_ok:
                try:
                    with get_db_cursor(commit=False, dictionary=True) as (cursor, _):
                        cursor.execute(base_sql)
                        return cursor.fetchall() or []
                except Exception as retry_err:
                    logger.error("Failed to fetch joined feedback after initialization: %s", retry_err)
        logger.error("Failed to fetch joined feedback: %s", err)
        return []
    except Exception as err:
        logger.error("Failed to fetch joined feedback: %s", err)
        return []
