import os
from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor

# Paths
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'schema.sql')
SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'app.db')
PROFILE_COLUMNS = {
    'full_name': 'TEXT',
    'bio': 'TEXT',
    'avatar_url': 'TEXT',
    'google_url': 'TEXT',
    'facebook_url': 'TEXT',
    'linkedin_url': 'TEXT',
    'github_url': 'TEXT',
}


def get_conn():
    """Return a DB connection.

    Uses PostgreSQL when DATABASE_URL is set, otherwise uses SQLite.
    """
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        return psycopg2.connect(db_url, cursor_factory=RealDictCursor)

    import sqlite3
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _is_sqlite_connection(conn) -> bool:
    return 'sqlite3' in type(conn).__module__


def _sqlite_schema_needs_reset(conn) -> bool:
    """Detect legacy SQLite tables created from PostgreSQL syntax."""
    try:
        users_table = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'").fetchone()
        if not users_table:
            return False

        columns = conn.execute('PRAGMA table_info(users)').fetchall()
        id_column = next((col for col in columns if col[1] == 'id'), None)
        if not id_column:
            return True

        # Legacy DBs created `SERIAL PRIMARY KEY`, which breaks inserts in SQLite.
        return str(id_column[2]).upper() != 'INTEGER'
    except Exception:
        return True


def _adapt_query(query: str, conn):
    """Adjust query placeholders based on DB driver.

    psycopg2 uses %s, sqlite3 uses ?.
    """

    if 'sqlite3' in type(conn).__module__:
        return query.replace('%s', '?')
    return query


def execute(query, params=None, fetchone=False, fetchall=False, commit=False, return_lastrowid=False):
    """Execute a SQL query in a safe, parameterized way.

    Args:
        query: SQL query string with %s placeholders.
        params: Tuple of parameters.
        fetchone: Return a single row.
        fetchall: Return all rows.
        commit: Commit transaction.
        return_lastrowid: Return the last inserted row ID when committing.
    """
    params = params or ()
    conn = get_conn()
    cur = conn.cursor()

    try:
        q = _adapt_query(query, conn)
        cur.execute(q, params)
        lastrowid = None
        if commit:
            conn.commit()
            if return_lastrowid:
                # sqlite exposes lastrowid on cursor
                if hasattr(cur, 'lastrowid') and cur.lastrowid:
                    lastrowid = cur.lastrowid
                # psycopg2 can return via RETURNING clause if used by the caller
        if fetchone:
            return cur.fetchone()
        if fetchall:
            return cur.fetchall()
        if return_lastrowid:
            return lastrowid
    finally:
        cur.close()
        conn.close()


def init_db():
    """Initialize the database schema from schema.sql."""
    conn = get_conn()
    cur = conn.cursor()

    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        sql = f.read()

    if _is_sqlite_connection(conn) and _sqlite_schema_needs_reset(conn):
        cur.close()
        conn.close()

        if os.path.exists(SQLITE_DB_PATH):
            backup_path = f"{SQLITE_DB_PATH}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
            os.replace(SQLITE_DB_PATH, backup_path)

        conn = get_conn()
        cur = conn.cursor()

    if _is_sqlite_connection(conn):
        sqlite_sql = (
            sql.replace('SERIAL PRIMARY KEY', 'INTEGER PRIMARY KEY AUTOINCREMENT')
            .replace('JSONB', 'TEXT')
            .replace('BOOLEAN DEFAULT FALSE', 'INTEGER DEFAULT 0')
        )
        conn.executescript(sqlite_sql)
    else:
        # psycopg2 cannot execute multiple statements at once
        statements = [s.strip() for s in sql.split(';') if s.strip()]
        for stmt in statements:
            cur.execute(stmt)

    conn.commit()
    _ensure_user_profile_columns(conn)
    cur.close()
    conn.close()


def _ensure_user_profile_columns(conn):
    """Add profile-related columns when running against older local databases."""
    cur = conn.cursor()
    try:
        if _is_sqlite_connection(conn):
            existing = {row[1] for row in conn.execute('PRAGMA table_info(users)').fetchall()}
            for column, definition in PROFILE_COLUMNS.items():
                if column not in existing:
                    conn.execute(f'ALTER TABLE users ADD COLUMN {column} {definition}')
        else:
            cur.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'users'
                """
            )
            existing = {row['column_name'] if isinstance(row, dict) else row[0] for row in cur.fetchall()}
            for column in PROFILE_COLUMNS:
                if column not in existing:
                    cur.execute(f'ALTER TABLE users ADD COLUMN {column} TEXT')
        conn.commit()
    finally:
        cur.close()
