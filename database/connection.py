import psycopg2
from psycopg2 import pool
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT, ISOLATION_LEVEL_DEFAULT
from database.support_queries import CREATE_CASE_TABLE
from config import settings

class Database:
    def __init__(self):
        self.connection_pool = psycopg2.pool.SimpleConnectionPool(
            1, 10,
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password
        )

    def get_connection(self, autocommit=False):
        conn = self.connection_pool.getconn()
        if autocommit:
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return conn

    def return_connection(self, connection):
        connection.set_isolation_level(ISOLATION_LEVEL_DEFAULT)
        self.connection_pool.putconn(connection)

    def close_all_connections(self):
        self.connection_pool.closeall()

db = Database()

async def execute(query, params=None, fetch_one=False, fetch_all=False, autocommit=False):
    conn = db.get_connection(autocommit=autocommit)
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            if fetch_one:
                result = cursor.fetchone()
            elif fetch_all:
                result = cursor.fetchall()
            else:
                result = None
            if not autocommit:
                conn.commit()
            return result
    except Exception as e:
        if not autocommit:
            conn.rollback()
        raise e
    finally:
        db.return_connection(conn)

async def drop_database(db_name: str):
    """Drop a database if it exists"""
    # Connect to default 'postgres' database for admin operations
    admin_conn = psycopg2.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database='postgres'
    )
    admin_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    try:
        with admin_conn.cursor() as cursor:
            cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
    finally:
        admin_conn.close()

async def create_database(db_name: str):
    """Create a new database"""
    # Connect to default 'postgres' database for admin operations
    admin_conn = psycopg2.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database='postgres'
    )
    admin_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    try:
        with admin_conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE {db_name}")
    finally:
        admin_conn.close()

async def create_tables():
    """Create tables in the current database"""
    await execute(CREATE_CASE_TABLE)