import psycopg2
from models.abstract_repo import AbstractRepository, connection_wrapper
from exceptions import DatabaseError

class CVRepository(AbstractRepository):
    table_name = 'cvs'
    pk_name = 'cv_id'

    @connection_wrapper
    def insert(self, conn, cursor, cand_id, score, structure, contact_info, work_experience, education, skills, languages, length):
        try:
            cursor.execute("""
                INSERT INTO cvs (cand_id, score, structure, contact_info, work_experience, education, skills, languages, length)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                """, (cand_id, score, structure, contact_info, work_experience, education, skills, languages, length))
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            conn.rollback()
            raise DatabaseError(error)
        
    @connection_wrapper
    def get(self, conn, cursor, cand_id):
        cursor.execute("SELECT * FROM cvs WHERE cand_id = %s;", (cand_id, ))
        return cursor.fetchone()
    
    @connection_wrapper
    def delete(self, conn, cursor, cand_id):
        cursor.execute("DELETE FROM cvs WHERE cand_id = %s;", (cand_id, ))
        conn.commit()
