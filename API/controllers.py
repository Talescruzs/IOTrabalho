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
