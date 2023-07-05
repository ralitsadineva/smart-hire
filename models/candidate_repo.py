import psycopg2
from models.abstract_repo import AbstractRepository, connection_wrapper
from exceptions import DatabaseError

class CandidateRepository(AbstractRepository):
    table_name = 'candidates'
    pk_name = 'cand_id'

    @connection_wrapper
    def insert(self, conn, cursor, pos_id, first_name, last_name, email):
        try:
            cursor.execute("""
                INSERT INTO candidates (pos_id, first_name, last_name, email)
                VALUES (%s, %s, %s, %s);
                """, (pos_id, first_name, last_name, email))
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            conn.rollback()
            raise DatabaseError(error)

    @connection_wrapper
    def get_all_for_pos(self, conn, cursor, pos_id):
        cursor.execute("""
            SELECT candidates.*, cvs.score
            FROM candidates
            LEFT JOIN cvs ON candidates.cand_id = cvs.cand_id
            WHERE candidates.pos_id = %s;
            """, (pos_id, ))
        return cursor.fetchall()

    @connection_wrapper
    def get_all(self, conn, cursor):
        cursor.execute("SELECT * FROM candidates;")
        return cursor.fetchall()

    @connection_wrapper
    def update(self, conn, cursor, cand_id, email, phone_number, address, postal_code, city, country, date_of_birth):
        try:
            cursor.execute("""
                UPDATE candidates
                SET email = %s, phone_number = %s, address = %s, postal_code = %s, city = %s, country = %s, date_of_birth = %s, last_updated = CURRENT_TIMESTAMP
                WHERE cand_id = %s;
                """, (email, phone_number, address, postal_code, city, country, date_of_birth, cand_id))
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            conn.rollback()
            raise DatabaseError(error)

    @connection_wrapper
    def last_added(self, conn, cursor):
        cursor.execute("""
            SELECT candidates.*, positions.title, cvs.score, mls.motivation_lvl
            FROM candidates
            LEFT JOIN positions ON candidates.pos_id = positions.pos_id
            LEFT JOIN cvs ON candidates.cand_id = cvs.cand_id
            LEFT JOIN mls ON candidates.cand_id = mls.cand_id
            WHERE positions.active = TRUE
            ORDER BY candidates.created DESC
            LIMIT 5;
            """)
        return cursor.fetchall()

    @connection_wrapper
    def last_updated(self, conn, cursor):
        cursor.execute("""
            SELECT candidates.*, positions.title, cvs.score, mls.motivation_lvl
            FROM candidates
            LEFT JOIN positions ON candidates.pos_id = positions.pos_id
            LEFT JOIN cvs ON candidates.cand_id = cvs.cand_id
            LEFT JOIN mls ON candidates.cand_id = mls.cand_id
            WHERE positions.active = TRUE
            ORDER BY candidates.last_updated DESC
            LIMIT 5;
            """)
        return cursor.fetchall()

    @connection_wrapper
    def with_highest_cv_score(self, conn, cursor):
        cursor.execute("""
            SELECT candidates.*, positions.title, cvs.score, mls.motivation_lvl
            FROM candidates
            LEFT JOIN positions ON candidates.pos_id = positions.pos_id
            JOIN cvs ON candidates.cand_id = cvs.cand_id
            LEFT JOIN mls ON candidates.cand_id = mls.cand_id
            WHERE positions.active = TRUE
            ORDER BY cvs.score DESC
            LIMIT 5;
            """)
        return cursor.fetchall()

    @connection_wrapper
    def with_highest_motivation_lvl(self, conn, cursor):
        cursor.execute("""
            SELECT candidates.*, positions.title, cvs.score, mls.motivation_lvl
            FROM candidates
            LEFT JOIN positions ON candidates.pos_id = positions.pos_id
            LEFT JOIN cvs ON candidates.cand_id = cvs.cand_id
            JOIN mls ON candidates.cand_id = mls.cand_id
            WHERE positions.active = TRUE
            ORDER BY mls.motivation_lvl DESC
            LIMIT 5;
            """)
        return cursor.fetchall()
