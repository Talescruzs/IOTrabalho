from flask import jsonify, request

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
