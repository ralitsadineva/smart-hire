from abc import ABC
from config import get_database_params
from psycopg2 import pool
import psycopg2
import psycopg2.extras
from exceptions import DatabaseError, UniqueViolationError

class AbstractRepository(ABC):
    params = get_database_params()
    connection_pool = pool.SimpleConnectionPool(1, 10, **params)

    def get_connection(self):
        conn = self.connection_pool.getconn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        return conn, cursor

    def close_connection(self, conn, cursor):
        cursor.close()
        self.connection_pool.putconn(conn)
    
    @staticmethod
    def connection_wrapper(func):
        def wrapper(*args, **kwargs):
            kwargs['conn'], kwargs['cursor'] = args[0].get_connection()
            try:
                result =  func(*args, **kwargs)
            finally:
                args[0].close_connection(kwargs['conn'], kwargs['cursor'])
            return result
        return wrapper

    table_name = None
    pk_name = None

    @connection_wrapper
    def insert(self, *args, **kwargs):
        cursor = kwargs.get('cursor')
        conn = kwargs.get('conn')
        try:
            cursor.execute(f"""
                INSERT INTO {self.table_name} {self.insert_columns}
                VALUES {self.insert_values};
                """, args)
            conn.commit()
        except psycopg2.errors.UniqueViolation as e:
            conn.rollback()
            raise UniqueViolationError(e)
        except (Exception, psycopg2.DatabaseError) as error:
            conn.rollback()
            raise DatabaseError(error)

    @connection_wrapper
    def get(self, id, **kwargs):
        cursor = kwargs.get('cursor')
        cursor.execute(f"SELECT * FROM {self.table_name} WHERE {self.pk_name} = %s;", (id, ))
        return cursor.fetchone()
