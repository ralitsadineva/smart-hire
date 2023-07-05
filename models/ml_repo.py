import psycopg2
from models.abstract_repo import AbstractRepository, connection_wrapper
from exceptions import DatabaseError

class MLRepository(AbstractRepository):
    table_name = 'mls'
    pk_name = 'ml_id'

    @connection_wrapper
    def insert(self, conn, cursor, cand_id, motivation_lvl, sentiment, tone, length, grammar):
        try:
            cursor.execute("""
                INSERT INTO mls (cand_id, motivation_lvl, sentiment, tone, length, grammar)
                VALUES (%s, %s, %s, %s, %s, %s);
                """, (cand_id, motivation_lvl, sentiment, tone, length, grammar))
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            conn.rollback()
            raise DatabaseError(error)

    @connection_wrapper
    def get(self, conn, cursor, cand_id):
        cursor.execute("SELECT * FROM mls WHERE cand_id = %s;", (cand_id, ))
        return cursor.fetchone()

    @connection_wrapper
    def delete(self, conn, cursor, cand_id):
        cursor.execute("DELETE FROM mls WHERE cand_id = %s;", (cand_id, ))
        conn.commit()
