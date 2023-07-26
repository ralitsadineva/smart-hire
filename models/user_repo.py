import psycopg2
from models.abstract_repo import AbstractRepository
from exceptions import DatabaseError

class UserRepository(AbstractRepository):
    table_name = 'users'
    pk_name = 'id'
    insert_columns = '(email, username, password, type)'
    insert_values = '(%s, %s, %s, %s)'
    
    @AbstractRepository.connection_wrapper
    def get_by_username(self, username, **kwargs):
        cursor = kwargs.get('cursor')
        cursor.execute("SELECT * FROM users WHERE username = %s;", (username, ))
        return cursor.fetchone()

    @AbstractRepository.connection_wrapper
    def get_by_email(self, email, **kwargs):
        cursor = kwargs.get('cursor')
        cursor.execute("SELECT * FROM users WHERE email = %s;", (email, ))
        return cursor.fetchone()

    @AbstractRepository.connection_wrapper
    def update_password(self, password, id, **kwargs):
        cursor = kwargs.get('cursor')
        conn = kwargs.get('conn')
        try:
            cursor.execute("""
                UPDATE users
                SET password = %s, last_updated = CURRENT_TIMESTAMP
                WHERE id = %s;
                """, (password, id))
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            conn.rollback()
            raise DatabaseError(error)

    @AbstractRepository.connection_wrapper
    def update_avatar(self, avatar, id, **kwargs):
        cursor = kwargs.get('cursor')
        conn = kwargs.get('conn')
        try:
            cursor.execute("""
                UPDATE users
                SET avatar = %s, last_updated = CURRENT_TIMESTAMP
                WHERE id = %s;
                """, (avatar, id))
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            conn.rollback()
            raise DatabaseError(error)
    
    @AbstractRepository.connection_wrapper
    def update_signature(self, signature, id, **kwargs):
        cursor = kwargs.get('cursor')
        conn = kwargs.get('conn')
        try:
            cursor.execute("""
                UPDATE users
                SET signature = %s, last_updated = CURRENT_TIMESTAMP
                WHERE id = %s;
                """, (signature, id))
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            conn.rollback()
            raise DatabaseError(error)
    
    @AbstractRepository.connection_wrapper
    def update_company(self, company, id, **kwargs):
        cursor = kwargs.get('cursor')
        conn = kwargs.get('conn')
        try:
            cursor.execute("""
                UPDATE users
                SET company = %s, last_updated = CURRENT_TIMESTAMP
                WHERE id = %s;
                """, (company, id))
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            conn.rollback()
            raise DatabaseError(error)
