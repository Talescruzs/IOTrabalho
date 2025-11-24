#!/usr/bin/env python3
"""
Script para testar se os dados estão sendo salvos no banco de dados MySQL
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Carrega variáveis de ambiente
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
    print(f"✓ Variáveis carregadas de {env_path}\n")
except ImportError:
    print("AVISO: python-dotenv não instalado\n")

try:
    import mysql.connector
except ImportError:
    print("ERRO: mysql-connector-python não instalado")
    print("Instale com: pip install mysql-connector-python")
    sys.exit(1)

MYSQL_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'tales'),
    'password': os.environ.get('DB_PASSWORD', 'senha123'),
    'port': int(os.environ.get('DB_PORT', '3306')),
    'database': os.environ.get('DB_NAME', 'ioTabelas')
}

def test_connection():
    """Testa conexão com o banco"""
    print("="*60)
    print("TESTE DE CONEXÃO COM BANCO DE DADOS")
    print("="*60)
    print(f"Host: {MYSQL_CONFIG['host']}")
    print(f"Porta: {MYSQL_CONFIG['port']}")
    print(f"Usuário: {MYSQL_CONFIG['user']}")
    print(f"Banco: {MYSQL_CONFIG['database']}")
    print("="*60 + "\n")
    
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        print("✓ Conexão estabelecida com sucesso!\n")
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Erro ao conectar: {e}\n")
        return False

def list_esps():
    """Lista todas as ESPs registradas"""
    print("="*60)
    print("ESPs REGISTRADAS")
    print("="*60)
    
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cur = conn.cursor()
        
        cur.execute("SELECT id, nome, ip_address FROM esps ORDER BY id")
        rows = cur.fetchall()
        
        if rows:
            print(f"{'ID':<5} {'Nome':<25} {'IP':<15}")
            print("-" * 60)
            for row in rows:
                esp_id, nome, ip = row
                ip_display = ip if ip else "N/A"
                print(f"{esp_id:<5} {nome:<25} {ip_display:<15}")
            print(f"\nTotal: {len(rows)} ESP(s) registrada(s)\n")
        else:
            print("Nenhuma ESP registrada ainda.\n")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ Erro ao listar ESPs: {e}\n")

def list_sensors():
    """Lista todos os sensores cadastrados"""
    print("="*60)
    print("SENSORES CADASTRADOS")
    print("="*60)
    
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cur = conn.cursor()
        
        cur.execute("SELECT id, nome FROM sensores ORDER BY id")
        rows = cur.fetchall()
        
        if rows:
            print(f"{'ID':<5} {'Nome':<30}")
            print("-" * 60)
            for row in rows:
                sensor_id, nome = row
                print(f"{sensor_id:<5} {nome:<30}")
            print(f"\nTotal: {len(rows)} sensor(es) cadastrado(s)\n")
        else:
            print("Nenhum sensor cadastrado ainda.\n")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ Erro ao listar sensores: {e}\n")

def list_all_tables():
    """Lista todas as tabelas do banco de dados e seus conteúdos"""
    print("="*60)
    print("TODAS AS TABELAS DO BANCO")
    print("="*60 + "\n")
    
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cur = conn.cursor()
        
        # Lista todas as tabelas
        cur.execute("SHOW TABLES")
        tables = cur.fetchall()
        
        if not tables:
            print("Nenhuma tabela encontrada no banco.\n")
            cur.close()
            conn.close()
            return
        
        print(f"Banco: {MYSQL_CONFIG['database']}")
        print(f"Total de tabelas: {len(tables)}\n")
        
        # Para cada tabela, mostra estrutura e dados
        for (table_name,) in tables:
            print("─" * 60)
            print(f"📊 TABELA: {table_name}")
            print("─" * 60)
            
            # Mostra estrutura da tabela
            cur.execute(f"DESCRIBE {table_name}")
            columns = cur.fetchall()
            
            print("\n🔧 Estrutura:")
            print(f"{'Campo':<20} {'Tipo':<20} {'Null':<6} {'Key':<6} {'Default':<10}")
            print("-" * 60)
            for col in columns:
                field, type_, null, key, default, extra = col
                default_str = str(default) if default else "-"
                print(f"{field:<20} {type_:<20} {null:<6} {key:<6} {default_str:<10}")
            
            # Conta registros
            cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cur.fetchone()[0]
            
            print(f"\n📝 Total de registros: {count}")
            
            # Mostra dados (limitado a 10 registros)
            if count > 0:
                cur.execute(f"SELECT * FROM {table_name} LIMIT 10")
                rows = cur.fetchall()
                
                # Pega nomes das colunas
                col_names = [desc[0] for desc in cur.description]
                
                print(f"\n📄 Primeiros {min(count, 10)} registros:")
                
                # Calcula largura das colunas
                col_widths = []
                for i, col_name in enumerate(col_names):
                    max_width = len(col_name)
                    for row in rows:
                        val_len = len(str(row[i]))
                        if val_len > max_width:
                            max_width = val_len
                    col_widths.append(min(max_width, 30))  # Limita a 30 chars
                
                # Header
                header = " | ".join(f"{col_names[i]:<{col_widths[i]}}" for i in range(len(col_names)))
                print(header)
                print("-" * len(header))
                
                # Dados
                for row in rows:
                    row_str = " | ".join(
                        f"{str(row[i]):<{col_widths[i]}.{col_widths[i]}}" 
                        for i in range(len(row))
                    )
                    print(row_str)
                
                if count > 10:
                    print(f"\n... e mais {count - 10} registro(s)")
            
            print("\n")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ Erro ao listar tabelas: {e}\n")
        import traceback
        traceback.print_exc()

def list_recent_readings(limit=10):
    """Lista as leituras mais recentes"""
    print("="*60)
    print(f"ÚLTIMAS {limit} LEITURAS")
    print("="*60)
    
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cur = conn.cursor()
        
        query = """
        SELECT 
            l.id,
            s.nome as sensor,
            e.nome as esp,
            l.timestamp
        FROM leituras l
        JOIN sensores s ON l.sensor_id = s.id
        JOIN esps e ON l.esp_id = e.id
        ORDER BY l.timestamp DESC
        LIMIT %s
        """
        
        cur.execute(query, (limit,))
        rows = cur.fetchall()
        
        if rows:
            print(f"{'ID':<8} {'Sensor':<20} {'ESP':<20} {'Timestamp':<20}")
            print("-" * 60)
            for row in rows:
                leitura_id, sensor, esp, timestamp = row
                print(f"{leitura_id:<8} {sensor:<20} {esp:<20} {str(timestamp):<20}")
            print(f"\nTotal: {len(rows)} leitura(s)\n")
        else:
            print("Nenhuma leitura encontrada ainda.\n")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ Erro ao listar leituras: {e}\n")

def show_reading_details(leitura_id):
    """Mostra os detalhes de uma leitura específica"""
    print("="*60)
    print(f"DETALHES DA LEITURA #{leitura_id}")
    print("="*60)
    
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cur = conn.cursor()
        
        # Busca valores da leitura
        query = """
        SELECT campo, valor
        FROM valores
        WHERE leitura_id = %s
        ORDER BY campo
        """
        
        cur.execute(query, (leitura_id,))
        rows = cur.fetchall()
        
        if rows:
            print(f"{'Campo':<20} {'Valor':<15}")
            print("-" * 60)
            for campo, valor in rows:
                print(f"{campo:<20} {valor:<15.2f}")
            print(f"\nTotal: {len(rows)} campo(s)\n")
        else:
            print(f"Nenhum valor encontrado para leitura #{leitura_id}\n")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ Erro ao buscar detalhes: {e}\n")

def main():
    print("\n" + "="*60)
    print("VERIFICADOR DE DADOS DO BANCO IOT")
    print("="*60 + "\n")
    
    # Verifica argumentos de linha de comando
    if len(sys.argv) > 1 and sys.argv[1] == '--all':
        # Modo detalhado: mostra todas as tabelas
        if not test_connection():
            print("Não foi possível conectar ao banco. Verifique as configurações.")
            return
        
        list_all_tables()
        
        print("="*60)
        print("FIM DO TESTE DETALHADO")
        print("="*60 + "\n")
        return
    
    # Testa conexão
    if not test_connection():
        print("Não foi possível conectar ao banco. Verifique as configurações.")
        return
    
    # Lista ESPs
    list_esps()
    
    # Lista sensores
    list_sensors()
    
    # Lista leituras recentes
    list_recent_readings(10)
    
    # Se houver leituras, mostra detalhes da mais recente
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT MAX(id) FROM leituras")
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        if result and result[0]:
            show_reading_details(result[0])
    except:
        pass
    
    print("="*60)
    print("FIM DO TESTE")
    print("="*60)
    print("\nDica: Use 'python test_database.py --all' para ver todas as tabelas\n")

if __name__ == "__main__":
    main()
