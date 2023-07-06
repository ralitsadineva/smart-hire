import psycopg2
from models.abstract_repo import AbstractRepository
from exceptions import DatabaseError

class CVRepository(AbstractRepository):
    table_name = 'cvs'
    pk_name = 'cv_id'

    @AbstractRepository.connection_wrapper
    def insert(self, cand_id, score, structure, contact_info, work_experience, education, skills, languages, length, **kwargs):
        cursor = kwargs.get('cursor')
        conn = kwargs.get('conn')
        try:
            cursor.execute("""
                INSERT INTO cvs (cand_id, score, structure, contact_info, work_experience, education, skills, languages, length)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                """, (cand_id, score, structure, contact_info, work_experience, education, skills, languages, length))
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            conn.rollback()
            raise DatabaseError(error)
        
    @AbstractRepository.connection_wrapper
    def get(self, cand_id, **kwargs):
        cursor = kwargs.get('cursor')
        cursor.execute("SELECT * FROM cvs WHERE cand_id = %s;", (cand_id, ))
        return cursor.fetchone()
    
    @AbstractRepository.connection_wrapper
    def delete(self, cand_id, **kwargs):
        cursor = kwargs.get('cursor')
        conn = kwargs.get('conn')
        cursor.execute("DELETE FROM cvs WHERE cand_id = %s;", (cand_id, ))
        conn.commit()
