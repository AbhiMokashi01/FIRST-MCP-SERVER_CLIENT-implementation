import psycopg
from psycopg.rows import dict_row

# PostgreSQL connection
def get_connection():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL not found in .env")

    return psycopg.connect(
        database_url,
        row_factory=dict_row
    )
