import os
import mysql.connector
from contextlib import contextmanager

MYSQL_CONFIG = {
    'host': os.environ.get('DB_HOST', 'db'),
    'user': os.environ.get('DB_USER', 'tales'),
    'password': os.environ.get('DB_PASSWORD', 'senha123'),
    'port': int(os.environ.get('DB_PORT', '3306')),
    'database': os.environ.get('DB_NAME', 'banco_atu')
}

@contextmanager
def get_db_connection():
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    try:
        yield conn
    finally:
        conn.close()

def insert_sensor_data(sensor_name, fields_dict):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM sensores WHERE nome = %s", (sensor_name,))
            row = cur.fetchone()
            if row:
                sensor_id = row[0]
            else:
                cur.execute("INSERT INTO sensores (nome) VALUES (%s)", (sensor_name,))
                sensor_id = cur.lastrowid
            cur.execute("INSERT INTO leituras (sensor_id) VALUES (%s)", (sensor_id,))
            leitura_id = cur.lastrowid
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
