import psycopg

from server.config import DATABASE_URL


class PostgresService:

    def __init__(self):
        self.connection = psycopg.connect(DATABASE_URL)

    def test_connection(self):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            result = cursor.fetchone()
            return result[0]

    def close(self):
        self.connection.close()