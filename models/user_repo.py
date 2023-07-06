import psycopg2
from models.abstract_repo import AbstractRepository
from exceptions import DatabaseError, UniqueViolationError

class UserRepository(AbstractRepository):
    table_name = 'users'
    pk_name = 'id'

    @AbstractRepository.connection_wrapper
    def insert(self, email, username, password, **kwargs):
        cursor = kwargs.get('cursor')
        conn = kwargs.get('conn')
        try:
            cursor.execute("""
                INSERT INTO users (email, username, password)
                VALUES (%s, %s, %s);
                """, (email, username, password))
            conn.commit()
        except psycopg2.errors.UniqueViolation as e:
            conn.rollback()
            raise UniqueViolationError(e)
        except (Exception, psycopg2.DatabaseError) as error:
            conn.rollback()
            raise DatabaseError(error)
    
    @AbstractRepository.connection_wrapper
    def insert_google(self, email, username, password, **kwargs):
        cursor = kwargs.get('cursor')
        conn = kwargs.get('conn')
        try:
            cursor.execute("""
                INSERT INTO users (email, username, password, type)
                VALUES (%s, %s, %s, '1');
                """, (email, username, password))
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            conn.rollback()
            raise DatabaseError(error)
    
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
    def update_password(self, password, username, **kwargs):
        cursor = kwargs.get('cursor')
        conn = kwargs.get('conn')
        try:
            cursor.execute("""
                UPDATE users
                SET password = %s
                WHERE username = %s;
                """, (password, username))
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            conn.rollback()
            raise DatabaseError(error)

    @AbstractRepository.connection_wrapper
    def update_avatar(self, avatar, username, **kwargs):
        cursor = kwargs.get('cursor')
        conn = kwargs.get('conn')
        try:
            cursor.execute("""
                UPDATE users
                SET avatar = %s
                WHERE username = %s;
                """, (avatar, username))
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            conn.rollback()
            raise DatabaseError(error)
