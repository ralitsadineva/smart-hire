import psycopg2
from config import get_database_params

class DatabaseError(Exception):
    pass

class UniqueViolationError(DatabaseError):
    pass

def create_tables():
    global conn, cursor
    params = get_database_params()
    conn = psycopg2.connect(**params)
    #print(conn)
    cursor = conn.cursor()
    #print(cursor)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(), 
            email VARCHAR(255) NOT NULL UNIQUE, 
            username VARCHAR(255) NOT NULL UNIQUE, 
            password BYTEA NOT NULL
        );
        """)
    conn.commit()

def insert_user(email, username, password):
    try:
        cursor.execute("""
            INSERT INTO users (email, username, password)
            VALUES (%s, %s, %s);
            """, (email, username, password))
        conn.commit()
    except psycopg2.errors.UniqueViolation as e:
        conn.rollback()
        raise UniqueViolationError(e)
    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()
        raise DatabaseError(error)

def get_user(username):
    cursor.execute("SELECT * FROM users WHERE username = %s;", (username, ))
    return cursor.fetchone()

def update_password(password, username):
    try:
        cursor.execute("""
            UPDATE users
            SET password = %s
            WHERE username = %s;
            """, (password, username))
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()
        raise DatabaseError(error)
