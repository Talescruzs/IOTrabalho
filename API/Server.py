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

# Validar e printar configurações MQTT
MQTT_BROKER = os.environ.get('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.environ.get('MQTT_PORT', 1883))
MQTT_TOPIC = os.environ.get('MQTT_TOPIC', 'iot/register')

print(f"[config] MQTT_BROKER={MQTT_BROKER}, MQTT_PORT={MQTT_PORT}, MQTT_TOPIC={MQTT_TOPIC}", flush=True)

# Inicializa o banco de dados MySQL e cria tabelas se não existirem
def init_db():
    try:
        import mysql.connector
    except ImportError:
        print("AVISO: mysql-connector-python não instalado, pulando init_db.", flush=True)
        print("Instale com: pip install mysql-connector-python", flush=True)
        return
    
    mysql_config = {
        'host': os.environ.get('DB_HOST', 'localhost'),
        'user': os.environ.get('DB_USER', 'tales'),
        'password': os.environ.get('DB_PASSWORD', 'senha123'),
        'port': int(os.environ.get('DB_PORT', '3306'))
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
                try:
                    cur.execute(statement)
                except mysql.connector.Error as err:
                    # Ignora erro de índice duplicado (código 1061)
                    if err.errno == 1061:
                        print(f"ℹ️  Índice já existe (ignorando): {err.msg}", flush=True)
                    else:
                        raise
        
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

# inicia mqtt listener (se disponível) - apenas no processo principal
if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    try:
        from API.mqtt_listener import start_background
        start_background()
    except Exception as e:
        print(f"AVISO: não foi possível iniciar mqtt_listener: {e}", flush=True)

# Cria o banco caso não exista
init_db()

app = Flask(__name__, template_folder='../Front/templates', static_folder='../Front/static')
CORS(app, supports_credentials=True)
print("CORS habilitado para todos os origins.", flush=True)
app.register_blueprint(api_bp)

if __name__ == "__main__":

    app.run(host='0.0.0.0', port=int(os.environ.get("API_PORT", "5000")), debug=True)