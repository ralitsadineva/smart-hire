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
            avatar VARCHAR(255) DEFAULT 'user.png',
            type CHAR NOT NULL DEFAULT '0' CHECK (type IN ('0', '1'))
        );
        """)  # type 0 = default, 1 = Google
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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cvs (
            cv_id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
            cand_id UUID NOT NULL REFERENCES candidates (cand_id),
            score INTEGER CHECK (score >= 0 AND score <= 100),
            structure INTEGER CHECK (structure > 0 AND structure <= 5),
            contact_info INTEGER CHECK (contact_info > 0 AND contact_info <= 5),
            work_experience INTEGER CHECK (work_experience > 0 AND work_experience <= 10),
            education INTEGER CHECK (education > 0 AND education <= 10),
            skills INTEGER CHECK (skills > 0 AND skills <= 10),
            languages INTEGER CHECK (languages > 0 AND languages <= 10),
            length INTEGER,
            created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """)
    conn.commit()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mls (
            ml_id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
            cand_id UUID NOT NULL REFERENCES candidates (cand_id),
            motivation_lvl INTEGER CHECK (motivation_lvl > 0 AND motivation_lvl <= 10),
            sentiment VARCHAR(255) CHECK (sentiment IN ('Positive', 'Negative', 'Neutral')),
            tone VARCHAR(255),
            length INTEGER,
            grammar VARCHAR(255),
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

def insert_google_user(email, username, password):
    conn, cursor = get_connection()
    try:
        cursor.execute("""
            INSERT INTO users (email, username, password, type)
            VALUES (%s, %s, %s, '1');
            """, (email, username, password))
        conn.commit()
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

def get_user_by_email(email):
    conn, cursor = get_connection()
    try:
        cursor.execute("SELECT * FROM users WHERE email = %s;", (email, ))
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

def insert_candidate(pos_id, first_name, last_name, email):
    conn, cursor = get_connection()
    try:
        cursor.execute("""
            INSERT INTO candidates (pos_id, first_name, last_name, email)
            VALUES (%s, %s, %s, %s);
            """, (pos_id, first_name, last_name, email))
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()
        raise DatabaseError(error)
    finally:
        close_connection(conn, cursor)

def get_candidate(cand_id):
    conn, cursor = get_connection()
    try:
        cursor.execute("SELECT * FROM candidates WHERE cand_id = %s;", (cand_id, ))
        return cursor.fetchone()
    finally:
        close_connection(conn, cursor)

def get_candidates(pos_id):
    conn, cursor = get_connection()
    try:
        cursor.execute("SELECT * FROM candidates WHERE pos_id = %s;", (pos_id, ))
        return cursor.fetchall()
    finally:
        close_connection(conn, cursor)

def get_all_candidates():
    conn, cursor = get_connection()
    try:
        cursor.execute("SELECT * FROM candidates;")
        return cursor.fetchall()
    finally:
        close_connection(conn, cursor)

def update_candidate(cand_id, email, phone_number, address, postal_code, city, country, date_of_birth):
    conn, cursor = get_connection()
    try:
        cursor.execute("""
            UPDATE candidates
            SET email = %s, phone_number = %s, address = %s, postal_code = %s, city = %s, country = %s, date_of_birth = %s
            WHERE cand_id = %s;
            """, (email, phone_number, address, postal_code, city, country, date_of_birth, cand_id))
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()
        raise DatabaseError(error)
    finally:
        close_connection(conn, cursor)

def insert_cv(cand_id, score, structure, contact_info, work_experience, education, skills, languages, length):
    conn, cursor = get_connection()
    try:
        cursor.execute("""
            INSERT INTO cvs (cand_id, score, structure, contact_info, work_experience, education, skills, languages, length)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (cand_id, score, structure, contact_info, work_experience, education, skills, languages, length))
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()
        raise DatabaseError(error)
    finally:
        close_connection(conn, cursor)

def get_cv(cand_id):
    conn, cursor = get_connection()
    try:
        cursor.execute("SELECT * FROM cvs WHERE cand_id = %s;", (cand_id, ))
        return cursor.fetchone()
    finally:
        close_connection(conn, cursor)

def del_cv(cand_id):
    conn, cursor = get_connection()
    try:
        cursor.execute("DELETE FROM cvs WHERE cand_id = %s;", (cand_id, ))
        conn.commit()
    finally:
        close_connection(conn, cursor)

def insert_ml(cand_id, motivation_lvl, sentiment, tone, length, grammar):
    conn, cursor = get_connection()
    try:
        cursor.execute("""
            INSERT INTO mls (cand_id, motivation_lvl, sentiment, tone, length, grammar)
            VALUES (%s, %s, %s, %s, %s, %s);
            """, (cand_id, motivation_lvl, sentiment, tone, length, grammar))
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()
        raise DatabaseError(error)
    finally:
        close_connection(conn, cursor)

def get_ml(cand_id):
    conn, cursor = get_connection()
    try:
        cursor.execute("SELECT * FROM mls WHERE cand_id = %s;", (cand_id, ))
        return cursor.fetchone()
    finally:
        close_connection(conn, cursor)

def del_ml(cand_id):
    conn, cursor = get_connection()
    try:
        cursor.execute("DELETE FROM mls WHERE cand_id = %s;", (cand_id, ))
        conn.commit()
    finally:
        close_connection(conn, cursor)
