import psycopg2
from models.abstract_repo import AbstractRepository
from exceptions import DatabaseError

class MLRepository(AbstractRepository):
    table_name = 'mls'
    pk_name = 'ml_id'

    @AbstractRepository.connection_wrapper
    def insert(self, cand_id, motivation_lvl, sentiment, tone, length, grammar, **kwargs):
        cursor = kwargs.get('cursor')
        conn = kwargs.get('conn')
        try:
            cursor.execute("""
                INSERT INTO mls (cand_id, motivation_lvl, sentiment, tone, length, grammar)
                VALUES (%s, %s, %s, %s, %s, %s);
                """, (cand_id, motivation_lvl, sentiment, tone, length, grammar))
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            conn.rollback()
            raise DatabaseError(error)

    @AbstractRepository.connection_wrapper
    def get(self, cand_id, **kwargs):
        cursor = kwargs.get('cursor')
        cursor.execute("SELECT * FROM mls WHERE cand_id = %s;", (cand_id, ))
        return cursor.fetchone()

    @AbstractRepository.connection_wrapper
    def delete(self, cand_id, **kwargs):
        cursor = kwargs.get('cursor')
        conn = kwargs.get('conn')
        cursor.execute("DELETE FROM mls WHERE cand_id = %s;", (cand_id, ))
        conn.commit()
