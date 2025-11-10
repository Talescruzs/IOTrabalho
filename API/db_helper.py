import os
import mysql.connector
from contextlib import contextmanager
from pathlib import Path

# Carrega .env
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    pass

MYSQL_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', ''),
    'port': int(os.environ.get('MYSQL_PORT', '3306')),
    'database': 'ioTabelas'
}

@contextmanager
def get_db_connection():
    """Context manager para conexões MySQL"""
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    try:
        yield conn
    finally:
        conn.close()

def insert_sensor_data(sensor_name, fields_dict):
    """
    Insere dados de sensor no banco MySQL
    
    Args:
        sensor_name: nome do sensor (ex: "motor")
        fields_dict: dicionário com campos e valores (ex: {"rpm": 1500, "temp": 25.5})
    
    Returns:
        leitura_id ou None se falhar
    """
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            # Busca ou cria sensor
            cur.execute("SELECT id FROM sensores WHERE nome = %s", (sensor_name,))
            row = cur.fetchone()
            if row:
                sensor_id = row[0]
            else:
                cur.execute("INSERT INTO sensores (nome) VALUES (%s)", (sensor_name,))
                sensor_id = cur.lastrowid
            
            # Cria leitura
            cur.execute("INSERT INTO leituras (sensor_id) VALUES (%s)", (sensor_id,))
            leitura_id = cur.lastrowid
            
            # Insere valores
            for campo, valor in fields_dict.items():
                cur.execute(
                    "INSERT INTO valores (leitura_id, campo, valor) VALUES (%s, %s, %s)",
                    (leitura_id, campo, float(valor))
                )
            
            conn.commit()
            return leitura_id
    except Exception as e:
        print(f"ERRO insert_sensor_data: {e}", flush=True)
        return None
