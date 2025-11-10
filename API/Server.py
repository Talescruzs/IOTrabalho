import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sqlite3
from pathlib import Path

# Inicializa o banco de dados local (SQLite) e cria tabelas se não existirem
def init_db():
    db_dir = Path(__file__).resolve().parent.parent / 'Banco'
    db_dir.mkdir(parents=True, exist_ok=True)
    db_path = db_dir / 'iot.db'

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    sql_file = db_dir / 'CreateDB.sql'
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    # executa múltiplas instruções do arquivo SQL
    cur.executescript(sql_script)
    

    conn.commit()
    conn.close()

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