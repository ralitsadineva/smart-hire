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
    
    def connection_wrapper(self, func):
        def wrapper(self, conn, cursor, *args, **kwargs):
            conn, cursor = self.get_connection()
            try:
                return func(self, conn, cursor, *args, **kwargs)
            finally:
                self.close_connection(conn, cursor)
        return wrapper

    table_name = None
    pk_name = None

    @connection_wrapper
    def get(self, conn, cursor, id):
        cursor.execute(f"SELECT * FROM {self.table_name} WHERE {self.pk_name} = %s;", (id, ))
        return cursor.fetchone()
