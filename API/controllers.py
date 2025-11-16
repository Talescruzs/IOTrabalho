from flask import jsonify, request
import os
from datetime import datetime, timezone
import json

last_esp_payload = {}

def get_data():
    # Exemplo de dados
    data = {"message": "Dados da API", "values": [1, 2, 3]}
    return jsonify(data)

def control_command():
    payload = request.get_json(silent=True) or {}
    action = payload.get('action')
    event = payload.get('event')

    # Loga no terminal a direção e o evento (down/up)
    print(f"Direção: {action} | Evento: {event}", flush=True)

    # Aqui você poderá integrar com a ESP32 (MQTT/HTTP/Serial)
    # Por ora, apenas ecoa a solicitação
    return jsonify({
        "ok": True,
        "received": {"action": action, "event": event}
    })

def esp_status():
    host_default = os.environ.get("ESP32_HOST", "192.168.0.50")  # ajuste conforme sua rede
    host = request.args.get("host", host_default)
    url = f"http://{host}/status"
    data = {}
    try:
        try:
            import requests
            r = requests.get(url, timeout=2)
            if r.status_code == 200:
                data = r.json()
            else:
                return jsonify({"ok": False, "error": f"HTTP {r.status_code}", "host": host}), 502
        except ImportError:
            # fallback sem requests
            import urllib.request, json
            with urllib.request.urlopen(url, timeout=2) as resp:
                raw = resp.read().decode()
                data = json.loads(raw)
        return jsonify({"ok": True, "host": host, "data": data})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e), "host": host}), 500

def ingest_status():
    global last_esp_payload
    
    # Log de debug
    print(f"[ingest] Requisição de {request.remote_addr}", flush=True)
    print(f"[ingest] Headers: {dict(request.headers)}", flush=True)
    print(f"[ingest] Raw data: {request.get_data(as_text=True)}", flush=True)
    
    payload = request.get_json(silent=True)
    
    if payload is None:
        print("[ingest] ERRO: JSON inválido ou vazio", flush=True)
        return jsonify({"ok": False, "error": "JSON inválido ou vazio"}), 400
    
    if not isinstance(payload, dict):
        print(f"[ingest] ERRO: Payload não é dict: {type(payload)}", flush=True)
        return jsonify({"ok": False, "error": "JSON deve ser um objeto"}), 400
    
    last_esp_payload = {
        "received_at": datetime.now(timezone.utc).isoformat(),
        "remote_addr": request.remote_addr,
        "data": payload
    }
    
    print(f"[ingest] ✓ Payload armazenado: {json.dumps(payload, indent=2)}", flush=True)
    return jsonify({"ok": True})

def esp_latest():
    if not last_esp_payload:
        return jsonify({"ok": False, "error": "Sem dados ainda"}), 404
    return jsonify({"ok": True, "payload": last_esp_payload})

def get_chart_data():
    """Retorna dados agregados para gráficos"""
    try:
        from API.db_helper import get_db_connection
    except ImportError:
        return jsonify({"ok": False, "error": "db_helper não disponível"}), 500
    
    try:
        with get_db_connection() as conn:
            cur = conn.cursor(dictionary=True)
            
            # 1. Contagem de leituras por ESP
            cur.execute("""
                SELECT e.nome as esp, COUNT(l.id) as total_leituras
                FROM esps e
                LEFT JOIN leituras l ON e.id = l.esp_id
                GROUP BY e.id, e.nome
                ORDER BY total_leituras DESC
            """)
            leituras_por_esp = cur.fetchall()
            
            # 2. Contagem de leituras por sensor
            cur.execute("""
                SELECT s.nome as sensor, COUNT(l.id) as total_leituras
                FROM sensores s
                LEFT JOIN leituras l ON s.id = l.sensor_id
                GROUP BY s.id, s.nome
                ORDER BY total_leituras DESC
            """)
            leituras_por_sensor = cur.fetchall()
            
            # 3. Últimas leituras (série temporal)
            cur.execute("""
                SELECT 
                    l.id,
                    l.timestamp,
                    s.nome as sensor,
                    e.nome as esp
                FROM leituras l
                JOIN sensores s ON l.sensor_id = s.id
                JOIN esps e ON l.esp_id = e.id
                ORDER BY l.timestamp DESC
                LIMIT 100
            """)
            ultimas_leituras = cur.fetchall()
            
            # Converter datetime para string ISO
            for leitura in ultimas_leituras:
                if leitura['timestamp']:
                    leitura['timestamp'] = leitura['timestamp'].isoformat()
            
            # 4. Dados dos sensores (últimos valores)
            cur.execute("""
                SELECT 
                    l.id as leitura_id,
                    s.nome as sensor,
                    l.timestamp,
                    v.campo,
                    v.valor
                FROM leituras l
                JOIN sensores s ON l.sensor_id = s.id
                JOIN valores v ON l.id = v.leitura_id
                WHERE l.id IN (
                    SELECT MAX(id) FROM leituras GROUP BY sensor_id
                )
                ORDER BY l.timestamp DESC
            """)
            valores_recentes = cur.fetchall()
            
            # Converter datetime
            for valor in valores_recentes:
                if valor['timestamp']:
                    valor['timestamp'] = valor['timestamp'].isoformat()
            
            cur.close()
            
            return jsonify({
                "ok": True,
                "data": {
                    "leituras_por_esp": leituras_por_esp,
                    "leituras_por_sensor": leituras_por_sensor,
                    "ultimas_leituras": ultimas_leituras,
                    "valores_recentes": valores_recentes
                }
            })
            
    except Exception as e:
        print(f"[chart_data] ERRO: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)}), 500

def get_sensor_history():
    """Retorna histórico de um sensor específico"""
    sensor_name = request.args.get('sensor')
    limit = int(request.args.get('limit', 50))
    
    if not sensor_name:
        return jsonify({"ok": False, "error": "Parâmetro 'sensor' é obrigatório"}), 400
    
    try:
        from API.db_helper import get_db_connection
    except ImportError:
        return jsonify({"ok": False, "error": "db_helper não disponível"}), 500
    
    try:
        with get_db_connection() as conn:
            cur = conn.cursor(dictionary=True)
            
            # Busca histórico do sensor
            cur.execute("""
                SELECT 
                    l.id as leitura_id,
                    l.timestamp,
                    e.nome as esp,
                    v.campo,
                    v.valor
                FROM leituras l
                JOIN sensores s ON l.sensor_id = s.id
                JOIN esps e ON l.esp_id = e.id
                JOIN valores v ON l.id = v.leitura_id
                WHERE s.nome = %s
                ORDER BY l.timestamp DESC
                LIMIT %s
            """, (sensor_name, limit))
            
            historico = cur.fetchall()
            
            # Converter datetime
            for item in historico:
                if item['timestamp']:
                    item['timestamp'] = item['timestamp'].isoformat()
            
            cur.close()
            
            return jsonify({
                "ok": True,
                "sensor": sensor_name,
                "count": len(historico),
                "data": historico
            })
            
    except Exception as e:
        print(f"[sensor_history] ERRO: {e}", flush=True)
        return jsonify({"ok": False, "error": str(e)}), 500

def get_detailed_readings():
    """Retorna leituras detalhadas com ESP, sensor e valores"""
    limit = int(request.args.get('limit', 50))
    
    try:
        from API.db_helper import get_db_connection
    except ImportError:
        return jsonify({"ok": False, "error": "db_helper não disponível"}), 500
    
    try:
        with get_db_connection() as conn:
            cur = conn.cursor(dictionary=True)
            
            # Busca leituras com todos os detalhes
            cur.execute("""
                SELECT 
                    l.id as leitura_id,
                    l.timestamp,
                    e.nome as esp,
                    s.nome as sensor
                FROM leituras l
                JOIN sensores s ON l.sensor_id = s.id
                JOIN esps e ON l.esp_id = e.id
                ORDER BY l.timestamp DESC
                LIMIT %s
            """, (limit,))
            
            leituras = cur.fetchall()
            
            # Para cada leitura, busca os valores
            for leitura in leituras:
                leitura_id = leitura['leitura_id']
                
                cur.execute("""
                    SELECT campo, valor
                    FROM valores
                    WHERE leitura_id = %s
                    ORDER BY campo
                """, (leitura_id,))
                
                valores = cur.fetchall()
                leitura['valores'] = valores
                
                # Converter datetime
                if leitura['timestamp']:
                    leitura['timestamp'] = leitura['timestamp'].isoformat()
            
            cur.close()
            
            return jsonify({
                "ok": True,
                "count": len(leituras),
                "data": leituras
            })
            
    except Exception as e:
        print(f"[detailed_readings] ERRO: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)}), 500
