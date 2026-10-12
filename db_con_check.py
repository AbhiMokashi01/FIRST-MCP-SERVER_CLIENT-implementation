import psycopg
from psycopg.rows import dict_row
import os


from dotenv import load_dotenv
load_dotenv()

# PostgreSQL connection
def get_connection():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL not found in .env")

    db= psycopg.connect(
        database_url,
        row_factory=dict_row
    )
    print(db)

    return db


def main():
    db=get_connection()
    with open("schema.sql", "r") as file:
            sql = file.read()
            print(db.execute(sql))
            db.commit()

   
    

if __name__=="__main__":
    main()