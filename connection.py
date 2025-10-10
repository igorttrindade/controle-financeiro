import psycopg2
from config import DATABASE_CONFIG

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DATABASE_CONFIG['host'],
            port=DATABASE_CONFIG['port'],
            user=DATABASE_CONFIG['user'],
            password=DATABASE_CONFIG['password'],
            database=DATABASE_CONFIG['database']
        )
        return conn
    except psycopg2.OperationalError as err:
        print(f"Erro ao conectar ao banco de dados: {err}")
        return None
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        return None