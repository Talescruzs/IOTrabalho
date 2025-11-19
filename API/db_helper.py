import os
import mysql.connector
from contextlib import contextmanager

MYSQL_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'tales'),
    'password': os.environ.get('DB_PASSWORD', 'senha123'),
    'port': int(os.environ.get('DB_PORT', '3306')),
    'database': os.environ.get('DB_NAME', 'ioTabelas')
}

@contextmanager
def get_db_connection():
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    try:
        yield conn
    finally:
        conn.close()

def register_or_update_esp(device_name, ip_address):
    """
    Registra ou atualiza uma ESP no banco de dados.
    Se já existir, atualiza o IP. Se não existir, cria um novo registro.
    
    Args:
        device_name (str): ID/nome do dispositivo ESP
        ip_address (str): Endereço IP do dispositivo
    
    Returns:
        int: ID da ESP no banco de dados, ou None se houver erro
    """
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            # Verifica se a ESP já existe
            cur.execute("SELECT id FROM esps WHERE nome = %s", (device_name,))
            row = cur.fetchone()
            
            if row:
                # ESP já existe, atualiza o IP
                esp_id = row[0]
                cur.execute(
                    "UPDATE esps SET ip_address = %s WHERE id = %s",
                    (ip_address, esp_id)
                )
                print(f"[db] ✓ ESP '{device_name}' atualizada com IP: {ip_address} (ID: {esp_id})", flush=True)
            else:
                # ESP não existe, cria novo registro
                cur.execute(
                    "INSERT INTO esps (nome, ip_address) VALUES (%s, %s)",
                    (device_name, ip_address)
                )
                esp_id = cur.lastrowid
                print(f"[db] ✓ Nova ESP '{device_name}' registrada com IP: {ip_address} (ID: {esp_id})", flush=True)
            
            conn.commit()
            cur.close()
            return esp_id
            
    except Exception as e:
        print(f"[db] ERRO ao registrar ESP: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return None

def insert_sensor_data(sensor_name, fields_dict, esp_id=None):
    """
    Insere dados de sensor no banco de dados.
    
    Args:
        sensor_name (str): Nome do sensor
        fields_dict (dict): Dicionário com campos e valores
        esp_id (int, optional): ID da ESP que enviou os dados
    
    Returns:
        int: ID da leitura criada, ou None se houver erro
    """
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            # Busca ou cria o sensor
            cur.execute("SELECT id FROM sensores WHERE nome = %s", (sensor_name,))
            row = cur.fetchone()
            if row:
                sensor_id = row[0]
            else:
                cur.execute("INSERT INTO sensores (nome) VALUES (%s)", (sensor_name,))
                sensor_id = cur.lastrowid
            
            # Cria a leitura (com ou sem esp_id)
            if esp_id:
                cur.execute(
                    "INSERT INTO leituras (sensor_id, esp_id) VALUES (%s, %s)",
                    (sensor_id, esp_id)
                )
            else:
                # Se não tiver esp_id, usa um valor padrão (1) ou NULL dependendo do schema
                # Como a FK é NOT NULL, vamos usar 1 como padrão
                cur.execute(
                    "INSERT INTO leituras (sensor_id, esp_id) VALUES (%s, %s)",
                    (sensor_id, 1)
                )
            
            leitura_id = cur.lastrowid
            
            # Insere os valores
            for campo, valor in fields_dict.items():
                cur.execute(
                    "INSERT INTO valores (leitura_id, campo, valor) VALUES (%s, %s, %s)",
                    (leitura_id, campo, float(valor))
                )
            
            conn.commit()
            cur.close()
            return leitura_id
            
    except Exception as e:
        print(f"[db] ERRO insert_sensor_data: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return None

def get_esp_id_by_name(device_id):
    """
    Busca o ID de uma ESP pelo nome.
    
    Args:
        device_id (str): Nome/ID do dispositivo
    
    Returns:
        int: ID da ESP no banco, ou None se não encontrada
    """
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM esps WHERE nome = %s", (device_id,))
            row = cur.fetchone()
            cur.close()
            return row[0] if row else None
    except Exception as e:
        print(f"[db] ERRO ao buscar ESP: {e}", flush=True)
        return None
