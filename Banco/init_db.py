import sys
import os
from pathlib import Path

# Carrega .env
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    print("AVISO: python-dotenv não instalado.", file=sys.stderr)

def init_database():
    """
    Inicializa o banco de dados MySQL executando o script CreateDB.sql
    Requisitos: pip install mysql-connector-python
    """
    try:
        import mysql.connector
    except ImportError:
        print("ERRO: mysql-connector-python não instalado.", file=sys.stderr)
        print("Instale com: pip install mysql-connector-python", file=sys.stderr)
        return False
    
    # Configurações de conexão (ajuste conforme necessário)
    mysql_config = {
        'host': os.environ.get('MYSQL_HOST', 'localhost'),
        'user': os.environ.get('MYSQL_USER', 'root'),
        'password': os.environ.get('MYSQL_PASSWORD', ''),
        'port': int(os.environ.get('MYSQL_PORT', '3306'))
    }
    
    db_dir = Path(__file__).resolve().parent
    sql_file = db_dir / 'CreateDB.sql'
    
    if not sql_file.exists():
        print(f"ERRO: Arquivo SQL não encontrado: {sql_file}", file=sys.stderr)
        return False
    
    try:
        print(f"Conectando ao MySQL em {mysql_config['host']}:{mysql_config['port']}...")
        conn = mysql.connector.connect(**mysql_config)
        cur = conn.cursor()
        
        # Lê o script SQL
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        print("Executando script SQL...")
        # Executa statement por statement (MySQL não suporta executescript)
        for statement in sql_script.split(';'):
            statement = statement.strip()
            if statement:
                print(f"  Executando: {statement[:50]}...")
                cur.execute(statement)
        
        conn.commit()
        print("✓ Banco de dados MySQL inicializado com sucesso!")
        
        # Verifica tabelas criadas
        cur.execute("USE ioTabelas;")
        cur.execute("SHOW TABLES;")
        tables = cur.fetchall()
        print(f"Tabelas criadas: {', '.join([t[0] for t in tables])}")
        
        cur.close()
        conn.close()
        return True
        
    except mysql.connector.Error as e:
        print(f"ERRO MySQL: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"ERRO inesperado: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    print("Variáveis de ambiente disponíveis:")
    print(f"  MYSQL_HOST (default: localhost)")
    print(f"  MYSQL_USER (default: root)")
    print(f"  MYSQL_PASSWORD (default: vazio)")
    print(f"  MYSQL_PORT (default: 3306)")
    print()
    success = init_database()
    sys.exit(0 if success else 1)
