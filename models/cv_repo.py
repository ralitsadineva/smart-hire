from models.abstract_repo import AbstractRepository

class CVRepository(AbstractRepository):
    table_name = 'cvs'
    pk_name = 'cv_id'
    insert_columns = '(cand_id, score, structure, contact_info, work_experience, education, skills, languages, length)'
    insert_values = '(%s, %s, %s, %s, %s, %s, %s, %s, %s)'
        
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
