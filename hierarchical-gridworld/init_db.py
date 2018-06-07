import sqlite3
from contextlib import closing

def init_database():
    with closing(sqlite3.connect("memoize.db")) as conn:
        c = conn.cursor()
        c.execute(
            "CREATE TABLE responses (input varchar, output varchar, source varchar, kind varchar)")
        conn.commit()

if __name__ == "__main__":
    init_database()
