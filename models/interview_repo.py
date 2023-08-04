import psycopg2
from models.abstract_repo import AbstractRepository
from exceptions import DatabaseError

class InterviewRepository(AbstractRepository):
    table_name = 'interviews'
    pk_name = 'id'
    insert_columns = '(cand_id, pos_id, score, notes, date)'
    insert_values = '(%s, %s, %s, %s, %s)'

    @AbstractRepository.connection_wrapper
    def update_score(self, score, id, **kwargs):
        cursor = kwargs.get('cursor')
        conn = kwargs.get('conn')
        try:
            cursor.execute("""
                UPDATE interviews
                SET score = %s, last_updated = CURRENT_TIMESTAMP
                WHERE id = %s;
                """, (score, id))
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            conn.rollback()
            raise DatabaseError(error)
    
    @AbstractRepository.connection_wrapper
    def update_notes(self, notes, id, **kwargs):
        cursor = kwargs.get('cursor')
        conn = kwargs.get('conn')
        try:
            cursor.execute("""
                UPDATE interviews
                SET notes = %s, last_updated = CURRENT_TIMESTAMP
                WHERE id = %s;
                """, (notes, id))
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            conn.rollback()
            raise DatabaseError(error)
    
    @AbstractRepository.connection_wrapper
    def update_date(self, date, id, **kwargs):
        cursor = kwargs.get('cursor')
        conn = kwargs.get('conn')
        try:
            cursor.execute("""
                UPDATE interviews
                SET date = %s, last_updated = CURRENT_TIMESTAMP
                WHERE id = %s;
                """, (date, id))
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            conn.rollback()
            raise DatabaseError(error)
    
    @AbstractRepository.connection_wrapper
    def get(self, cand_id, **kwargs):
        cursor = kwargs.get('cursor')
        cursor.execute("SELECT * FROM interviews WHERE cand_id = %s;", (cand_id, ))
        return cursor.fetchone()
