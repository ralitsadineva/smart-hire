import psycopg2
from models.abstract_repo import AbstractRepository, connection_wrapper
from exceptions import DatabaseError

class PositionRepository(AbstractRepository):
    table_name = 'positions'
    pk_name = 'pos_id'

    @connection_wrapper
    def insert(self, conn, cursor, user_id, title, description):
        try:
            cursor.execute("""
                INSERT INTO positions (user_id, title, description)
                VALUES (%s, %s, %s);
                """, (user_id, title, description))
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            conn.rollback()
            raise DatabaseError(error)

    @connection_wrapper
    def get_all_active(self, conn, cursor):
        cursor.execute("""
            SELECT positions.*, COUNT(candidates.cand_id) AS candidates_count
            FROM positions
            LEFT JOIN candidates ON positions.pos_id = candidates.pos_id
            WHERE active = TRUE
            GROUP BY positions.pos_id;
            """)
        return cursor.fetchall()

    @connection_wrapper
    def get_all_inactive(self, conn, cursor):
        cursor.execute("""
            SELECT positions.*, COUNT(candidates.cand_id) AS candidates_count
            FROM positions
            LEFT JOIN candidates ON positions.pos_id = candidates.pos_id
            WHERE active = FALSE
            GROUP BY positions.pos_id;
            """)
        return cursor.fetchall()

    @connection_wrapper
    def make_inactive(self, conn, cursor, pos_id):
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

    @connection_wrapper
    def make_active(self, conn, cursor, pos_id):
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

    @connection_wrapper
    def update(self, conn, cursor, pos_id, title, description):
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

    @connection_wrapper
    def last_added(self, conn, cursor):
        cursor.execute("""
            SELECT positions.*, COUNT(candidates.cand_id) AS candidates_count
            FROM positions
            LEFT JOIN candidates ON positions.pos_id = candidates.pos_id
            WHERE positions.active = TRUE
            GROUP BY positions.pos_id
            ORDER BY positions.created DESC
            LIMIT 5;
            """)
        return cursor.fetchall()

    @connection_wrapper
    def last_updated(self, conn, cursor):
        cursor.execute("""
            SELECT positions.*, COUNT(candidates.cand_id) AS candidates_count
            FROM positions
            LEFT JOIN candidates ON positions.pos_id = candidates.pos_id
            WHERE positions.active = TRUE
            GROUP BY positions.pos_id
            ORDER BY positions.last_updated DESC
            LIMIT 5;
            """)
        return cursor.fetchall()

    @connection_wrapper
    def with_most_candidates(self, conn, cursor):
        cursor.execute("""
            SELECT positions.*, COUNT(candidates.cand_id) AS candidates_count
            FROM positions
            LEFT JOIN candidates ON positions.pos_id = candidates.pos_id
            WHERE positions.active = TRUE
            GROUP BY positions.pos_id
            ORDER BY candidates_count DESC
            LIMIT 5;
            """)
        return cursor.fetchall()
