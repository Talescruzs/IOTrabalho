import os
import json
import threading
from datetime import datetime
try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None

# Importa funções do db_helper
try:
    from API.db_helper import register_or_update_esp, insert_sensor_data, get_esp_id_by_name
    DB_AVAILABLE = True
except ImportError:
    print("[mqtt] AVISO: db_helper não disponível, dados não serão salvos no BD", flush=True)
    DB_AVAILABLE = False

# Importa sistema de controle de acesso
try:
    from API.access_control import process_sensor_data, update_esp_ip
    ACCESS_CONTROL_AVAILABLE = True
except ImportError:
    print("[mqtt] AVISO: access_control não disponível", flush=True)
    ACCESS_CONTROL_AVAILABLE = False

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
            
            # Armazena IP do dispositivo em memória
            registered_devices[device_id] = ip
            print(f"✓ Dispositivo registrado em memória: {device_id} com IP: {ip}", flush=True)
            
            # Atualiza IP no sistema de controle de acesso
            if ACCESS_CONTROL_AVAILABLE:
                update_esp_ip(device_id, ip)
            
            # Registra/atualiza no banco de dados
            if DB_AVAILABLE:
                esp_id = register_or_update_esp(device_id, ip)
                if esp_id:
                    print(f"✓ Dispositivo salvo no banco com ID: {esp_id}", flush=True)
                else:
                    print(f"✗ Falha ao salvar dispositivo no banco", flush=True)
            else:
                print("[mqtt] Banco de dados não disponível, registro apenas em memória", flush=True)
            
            print(f"[mqtt] Dispositivos registrados: {registered_devices}", flush=True)
            
            # Enviar confirmação para tópico específico do device
            confirm_topic = f"iot/confirm/{device_id}"
            confirm_msg = json.dumps({
                "status": "registered",
                "device_id": device_id,
                "ip": ip,
                "timestamp": datetime.now().isoformat()
            })
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
                
                # Processa lógica do sistema de controle de acesso
                if ACCESS_CONTROL_AVAILABLE:
                    global client
                    process_sensor_data(device_id, sensor, fields, client)
                
                # Salva os dados no banco se disponível
                if DB_AVAILABLE:
                    # Busca o ID da ESP no banco
                    esp_id = get_esp_id_by_name(device_id)
                    
                    if esp_id:
                        # Insere os dados do sensor
                        leitura_id = insert_sensor_data(sensor, fields, esp_id)
                        if leitura_id:
                            print(f"[mqtt] ✓ Dados salvos no banco (leitura_id={leitura_id})", flush=True)
                        else:
                            print(f"[mqtt] ✗ Falha ao salvar dados no banco", flush=True)
                    else:
                        print(f"[mqtt] ⚠ ESP '{device_id}' não encontrada no banco, dados não salvos", flush=True)
                        print(f"[mqtt] Dica: Dispositivo precisa se registrar primeiro via tópico {MQTT_TOPIC}", flush=True)
                
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