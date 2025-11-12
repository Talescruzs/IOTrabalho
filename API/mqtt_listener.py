import os
import json
import threading
from datetime import datetime
try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None

# Dicionário para armazenar IPs registrados
registered_devices = {}

MQTT_BROKER = os.environ.get('MQTT_BROKER', '192.168.143.117')
MQTT_PORT = int(os.environ.get('MQTT_PORT', 1883))
MQTT_TOPIC = os.environ.get('MQTT_TOPIC', 'iot/register')

client = None

def on_connect(cl, userdata, flags, rc):
    print(f"[mqtt] conectado rc={rc} ao broker {MQTT_BROKER}:{MQTT_PORT}", flush=True)
    cl.subscribe(MQTT_TOPIC)
    cl.subscribe("iot/sensor/#")  # subscreve também em tópicos de sensores
    print(f"[mqtt] subscribed to {MQTT_TOPIC} e iot/sensor/#", flush=True)

def on_message(cl, userdata, msg):
    try:
        payload = msg.payload.decode('utf-8')
        
        # Print destacado quando receber mensagem
        print("\n" + "="*60, flush=True)
        print(f"[MQTT RECEBIDO] Tópico: {msg.topic}", flush=True)
        print(f"[MQTT RECEBIDO] Payload: {payload}", flush=True)
        print("="*60 + "\n", flush=True)
        
        # Validar payload antes de parsear JSON
        if not payload or payload.strip() == "":
            print("[mqtt] AVISO: Payload vazio recebido, ignorando.", flush=True)
            return
        
        data = json.loads(payload)
        
        # Detectar mensagem de registro de IP
        if 'device_id' in data and 'ip' in data:
            device_id = data.get('device_id', 'unknown')
            ip = data.get('ip', 'N/A')
            
            # Armazena IP do dispositivo
            registered_devices[device_id] = ip
            print(f"✓ Dispositivo registrado: {device_id} com IP: {ip}", flush=True)
            print(f"[mqtt] Dispositivos registrados: {registered_devices}", flush=True)
            
            # Enviar confirmação para tópico específico do device
            confirm_topic = f"iot/confirm/{device_id}"
            confirm_msg = "estou sentindo as minhas forcas indo embora"
            cl.publish(confirm_topic, confirm_msg)
            print(f"[mqtt] ✓ Confirmação enviada para tópico: {confirm_topic}", flush=True)
            
            return
        
        # Mensagem de sensor normal com device_id
        if 'device_id' in data:
            device_id = data.get('device_id')
            sensor = data.get('sensor', 'unknown')
            fields = data.get('data', {})
            
            if isinstance(fields, dict):
                print(f"[mqtt] Dados de {device_id}/{sensor}: {fields}", flush=True)
                
                # Enviar resposta para o dispositivo específico
                response_topic = f"iot/response/{device_id}"
                response_msg = json.dumps({
                    "status": "received",
                    "sensor": sensor,
                    "timestamp": datetime.now().isoformat()
                })
                cl.publish(response_topic, response_msg)
                print(f"[mqtt] ✓ Resposta enviada para {response_topic}", flush=True)
            else:
                print("[mqtt] campo 'data' não é dict, ignorando", flush=True)
                
    except json.JSONDecodeError as e:
        print(f"[mqtt] ERRO: Payload não é JSON válido -> {e}", flush=True)
        print(f"[mqtt] Payload recebido: '{payload}'", flush=True)
    except Exception as e:
        print(f"[mqtt] erro ao processar mensagem: {e}", flush=True)
        import traceback
        traceback.print_exc()

def run():
    global client
    if mqtt is None:
        print("paho-mqtt não instalado.", flush=True)
        return
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    except Exception as e:
        print(f"[mqtt] erro conectar ao broker {MQTT_BROKER}:{MQTT_PORT} -> {e}", flush=True)
        return
    client.loop_forever()

def start_background():
    t = threading.Thread(target=run, daemon=True)
    t.start()
    print(f"[mqtt] listener iniciado em thread daemon (broker={MQTT_BROKER}:{MQTT_PORT})", flush=True)
    return t

if __name__ == "__main__":
    start_background()
    import time
    while True:
        time.sleep(1)