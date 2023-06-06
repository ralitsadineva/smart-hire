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

def create_positions_table():
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

def insert_position(user_id, title, description):
    try:
        cursor.execute("""
            INSERT INTO positions (user_id, title, description)
            VALUES (%s, %s, %s);
            """, (user_id, title, description))
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()
        raise DatabaseError(error)

def get_positions(user_id):
    cursor.execute("SELECT * FROM positions WHERE user_id = %s;", (user_id, ))
    return cursor.fetchall()

def get_position(pos_id):
    cursor.execute("SELECT * FROM positions WHERE pos_id = %s;", (pos_id, ))
    return cursor.fetchone()

def make_position_inactive(pos_id):
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

def make_position_active(pos_id):
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

def update_position(pos_id, title, description):
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

def create_candidates_table():
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
