from models.abstract_repo import AbstractRepository

class MLRepository(AbstractRepository):
    table_name = 'mls'
    pk_name = 'ml_id'
    insert_columns = '(cand_id, motivation_lvl, sentiment, tone, length, grammar)'
    insert_values = '(%s, %s, %s, %s, %s, %s)'

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
