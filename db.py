import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()


# PostgreSQL connection
def get_connection():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL not found in .env")

    return psycopg.connect(
        database_url,
        row_factory=dict_row
    )



# 1. Save Note
def save_note(topic: str, content: str):
    """Accepts topic and content as arguments and updates the notes in the database"""
    topic = topic.strip()
    content = content.strip()

    if not topic or not content:
        raise ValueError("Topic and content cannot be empty")

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO notes (topic, content)
                VALUES (%s, %s)
                RETURNING id, topic, content, created_at
                """,
                (topic, content)
            )

            return cursor.fetchone()


# 2. List Notes
def list_notes():
    """returns details about notes to the agent"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, topic, content, created_at
                FROM notes
                ORDER BY created_at DESC, id DESC
                """
            )

            return cursor.fetchall()


# 3. Search Notes
def search_notes(keyword: str):
    """accepts keyword from user query and searchs for a notes in database"""
    keyword = keyword.strip()

    if not keyword:
        return []

    search_pattern = f"%{keyword}%"

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, topic, content, created_at
                FROM notes
                WHERE topic ILIKE %s
                   OR content ILIKE %s
                ORDER BY created_at DESC, id DESC
                """,
                (search_pattern, search_pattern)
            )

            return cursor.fetchall()
