from abc import ABC
from config import get_database_params
from psycopg2 import pool

class AbstractRepository(ABC):
    params = get_database_params()
    connection_pool = pool.SimpleConnectionPool(1, 10, **params)

    def get_connection(self):
        conn = self.connection_pool.getconn()
        cursor = conn.cursor()
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
    def get(self, id, **kwargs):
        cursor = kwargs.get('cursor')
        cursor.execute(f"SELECT * FROM {self.table_name} WHERE {self.pk_name} = %s;", (id, ))
        return cursor.fetchone()
