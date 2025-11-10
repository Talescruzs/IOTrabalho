import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pathlib import Path

# Carrega variáveis de ambiente do .env
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
    print(f"✓ Variáveis carregadas de {env_path}", flush=True)
except ImportError:
    print("AVISO: python-dotenv não instalado. Use: pip install python-dotenv", flush=True)

# Inicializa o banco de dados MySQL e cria tabelas se não existirem
def init_db():
    try:
        import mysql.connector
    except ImportError:
        print("AVISO: mysql-connector-python não instalado, pulando init_db.", flush=True)
        print("Instale com: pip install mysql-connector-python", flush=True)
        return
    
    mysql_config = {
        'host': os.environ.get('MYSQL_HOST', 'localhost'),
        'user': os.environ.get('MYSQL_USER', 'root'),
        'password': os.environ.get('MYSQL_PASSWORD', ''),
        'port': int(os.environ.get('MYSQL_PORT', '3306'))
    }
    
    print(f"Conectando ao MySQL: {mysql_config['user']}@{mysql_config['host']}:{mysql_config['port']}", flush=True)
    
    db_dir = Path(__file__).resolve().parent.parent / 'Banco'
    sql_file = db_dir / 'CreateDB.sql'
    
    try:
        conn = mysql.connector.connect(**mysql_config)
        cur = conn.cursor()
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        for statement in sql_script.split(';'):
            statement = statement.strip()
            if statement:
                cur.execute(statement)
        
        conn.commit()
        cur.close()
        conn.close()
        print("✓ Banco MySQL inicializado.", flush=True)
    except Exception as e:
        print(f"ERRO init_db MySQL: {e}", flush=True)

from flask import Flask
try:
    from flask_cors import CORS
except ImportError:
    def CORS(app, *args, **kwargs):
        print("Aviso: flask-cors não instalado; CORS desabilitado.", flush=True)
        return app
from routes import api_bp

# Cria o banco caso não exista
init_db()

app = Flask(__name__)
CORS(app, supports_credentials=True)
print("CORS habilitado para todos os origins.", flush=True)
app.register_blueprint(api_bp)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("API_PORT", "5000")), debug=True)