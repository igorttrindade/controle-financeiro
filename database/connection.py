import psycopg2

def get_db_connection(config):
    try:
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database=config['database']
        )
        return conn
    except psycopg2.OperationalError as err:
        print(f"Erro ao conectar ao banco de dados: {err}")
        return None
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        return None