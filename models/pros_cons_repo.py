from models.abstract_repo import AbstractRepository

class ProsConsRepository(AbstractRepository):
    table_name = 'pros_cons'
    pk_name = 'id'
    insert_columns = '(cand_id, pros, cons)'
    insert_values = '(%s, %s, %s)'

    @AbstractRepository.connection_wrapper
    def get(self, cand_id, **kwargs):
        cursor = kwargs.get('cursor')
        cursor.execute("SELECT * FROM pros_cons WHERE cand_id = %s;", (cand_id, ))
        return cursor.fetchone()
    
    @AbstractRepository.connection_wrapper
    def delete(self, cand_id, **kwargs):
        cursor = kwargs.get('cursor')
        conn = kwargs.get('conn')
        cursor.execute("DELETE FROM pros_cons WHERE cand_id = %s;", (cand_id, ))
        conn.commit()
