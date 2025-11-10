import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
try:
    from flask_cors import CORS
except ImportError:
    def CORS(app, *args, **kwargs):
        print("Aviso: flask-cors não instalado; CORS desabilitado.", flush=True)
        return app
from Front.routes import api_bp

app = Flask(__name__)
CORS(app, supports_credentials=True)
print("CORS (Front) habilitado para todos os origins.", flush=True)
app.register_blueprint(api_bp)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)