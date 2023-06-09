import psycopg2
from psycopg2 import pool
from config import get_database_params

class DatabaseError(Exception):
    pass

class UniqueViolationError(DatabaseError):
    pass

params = get_database_params()
connection_pool = pool.SimpleConnectionPool(1, 10, **params)

def get_connection():
    conn = connection_pool.getconn()
    cursor = conn.cursor()
    return conn, cursor

def close_connection(conn, cursor):
    cursor.close()
    connection_pool.putconn(conn)

def create_tables():
    conn, cursor = get_connection()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(), 
            email VARCHAR(255) NOT NULL UNIQUE, 
            username VARCHAR(255) NOT NULL UNIQUE, 
            password BYTEA NOT NULL,
            avatar VARCHAR(255) DEFAULT 'user.png'
        );
        """)
    conn.commit()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS positions (
            pos_id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(), 
            user_id UUID NOT NULL REFERENCES users (id), 
            title VARCHAR(255) NOT NULL, 
            description VARCHAR NOT NULL, 
            active BOOLEAN NOT NULL DEFAULT TRUE, 
            created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """)
    conn.commit()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            cand_id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(), 
            pos_id UUID NOT NULL REFERENCES positions (pos_id), 
            first_name VARCHAR(255) NOT NULL, 
            last_name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL, 
            phone_number VARCHAR(255), 
            address VARCHAR(255),
            postal_code VARCHAR(255),
            city VARCHAR(255),
            country VARCHAR(255),
            date_of_birth DATE,
            created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """)
    conn.commit()

    close_connection(conn, cursor)

def insert_user(email, username, password):
    conn, cursor = get_connection()
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
    finally:
        close_connection(conn, cursor)

def get_user(username):
    conn, cursor = get_connection()
    try:
        cursor.execute("SELECT * FROM users WHERE username = %s;", (username, ))
        return cursor.fetchone()
    finally:
        close_connection(conn, cursor)

def update_password(password, username):
    conn, cursor = get_connection()
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
    finally:
        close_connection(conn, cursor)

def update_avatar(avatar, username):
    conn, cursor = get_connection()
    try:
        cursor.execute("""
            UPDATE users
            SET avatar = %s
            WHERE username = %s;
            """, (avatar, username))
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()
        raise DatabaseError(error)
    finally:
        close_connection(conn, cursor)

def insert_position(user_id, title, description):
    conn, cursor = get_connection()
    try:
        cursor.execute("""
            INSERT INTO positions (user_id, title, description)
            VALUES (%s, %s, %s);
            """, (user_id, title, description))
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()
        raise DatabaseError(error)
    finally:
        close_connection(conn, cursor)

def get_positions(user_id):
    conn, cursor = get_connection()
    try:
        cursor.execute("SELECT * FROM positions WHERE user_id = %s;", (user_id, ))
        return cursor.fetchall()
    finally:
        close_connection(conn, cursor)

def get_position(pos_id):
    conn, cursor = get_connection()
    try:
        cursor.execute("SELECT * FROM positions WHERE pos_id = %s;", (pos_id, ))
        return cursor.fetchone()
    finally:
        close_connection(conn, cursor)

def make_position_inactive(pos_id):
    conn, cursor = get_connection()
    try:
        cursor.execute("""
            UPDATE positions
            SET active = FALSE, last_updated = CURRENT_TIMESTAMP
            WHERE pos_id = %s;
            """, (pos_id, ))
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()
        raise DatabaseError(error)
    finally:
        close_connection(conn, cursor)

def make_position_active(pos_id):
    conn, cursor = get_connection()
    try:
        cursor.execute("""
            UPDATE positions
            SET active = TRUE, last_updated = CURRENT_TIMESTAMP
            WHERE pos_id = %s;
            """, (pos_id, ))
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()
        raise DatabaseError(error)
    finally:
        close_connection(conn, cursor)

def update_position(pos_id, title, description):
    conn, cursor = get_connection()
    try:
        cursor.execute("""
            UPDATE positions
            SET title = %s, description = %s, last_updated = CURRENT_TIMESTAMP
            WHERE pos_id = %s;
            """, (title, description, pos_id))
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()
        raise DatabaseError(error)
    finally:
        close_connection(conn, cursor)