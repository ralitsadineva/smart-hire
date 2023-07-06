import psycopg2
from models.abstract_repo import AbstractRepository
from exceptions import DatabaseError

class PositionRepository(AbstractRepository):
    table_name = 'positions'
    pk_name = 'pos_id'
    insert_columns = '(user_id, title, description)'
    insert_values = '(%s, %s, %s)'

    @AbstractRepository.connection_wrapper
    def get_all_active(self, **kwargs):
        cursor = kwargs.get('cursor')
        cursor.execute("""
            SELECT positions.*, COUNT(candidates.cand_id) AS candidates_count
            FROM positions
            LEFT JOIN candidates ON positions.pos_id = candidates.pos_id
            WHERE active = TRUE
            GROUP BY positions.pos_id;
            """)
        return cursor.fetchall()

    @AbstractRepository.connection_wrapper
    def get_all_inactive(self, **kwargs):
        cursor = kwargs.get('cursor')
        cursor.execute("""
            SELECT positions.*, COUNT(candidates.cand_id) AS candidates_count
            FROM positions
            LEFT JOIN candidates ON positions.pos_id = candidates.pos_id
            WHERE active = FALSE
            GROUP BY positions.pos_id;
            """)
        return cursor.fetchall()

    @AbstractRepository.connection_wrapper
    def make_inactive(self, pos_id, **kwargs):
        cursor = kwargs.get('cursor')
        conn = kwargs.get('conn')
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

    @AbstractRepository.connection_wrapper
    def make_active(self, pos_id, **kwargs):
        cursor = kwargs.get('cursor')
        conn = kwargs.get('conn')
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

    @AbstractRepository.connection_wrapper
    def update(self, pos_id, title, description, **kwargs):
        cursor = kwargs.get('cursor')
        conn = kwargs.get('conn')
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

    @AbstractRepository.connection_wrapper
    def last_added(self, **kwargs):
        cursor = kwargs.get('cursor')
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

    @AbstractRepository.connection_wrapper
    def last_updated(self, **kwargs):
        cursor = kwargs.get('cursor')
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

    @AbstractRepository.connection_wrapper
    def with_most_candidates(self, **kwargs):
        cursor = kwargs.get('cursor')
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
