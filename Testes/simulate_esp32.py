#!/usr/bin/env python3
"""
Script de simulação da ESP32
Envia dados para o servidor via MQTT e HTTP, simulando o comportamento do dispositivo IoT.
"""

import time
import json
import random
import requests
import paho.mqtt.client as mqtt
from datetime import datetime
import os
from pathlib import Path

# Carrega variáveis de ambiente
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent / '.env'
    load_dotenv(dotenv_path=env_path)
    print(f"✓ Variáveis carregadas de {env_path}")
except ImportError:
    print("AVISO: python-dotenv não instalado")

# Configurações
DEVICE_ID = "esp32-simulator"
API_HOST = os.environ.get('API_HOST', 'localhost')
API_PORT = os.environ.get('API_PORT', '5000')
MQTT_BROKER = os.environ.get('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.environ.get('MQTT_PORT', 1883))
MQTT_TOPIC = os.environ.get('MQTT_TOPIC', 'iot/register')

# Simulação de dados do sensor
class SensorSimulator:
    def __init__(self):
        self.rpm = 1000.0
        self.temp = 25.0
        self.voltage = 12.0
        self.current = 2.5
        
    def update(self):
        """Atualiza valores dos sensores com variação aleatória"""
        self.rpm = max(0, self.rpm + random.uniform(-100, 150))
        self.rpm = min(4000, self.rpm)  # Limita a 4000 RPM
        
        self.temp = self.temp + random.uniform(-1, 1.5)
        self.temp = max(15, min(45, self.temp))  # Entre 15°C e 45°C
        
        self.voltage = 12.0 + random.uniform(-0.5, 0.5)
        self.current = 2.5 + random.uniform(-0.3, 0.3)
        
    def get_data(self):
        """Retorna dados atuais dos sensores"""
        return {
            "rpm": round(self.rpm, 2),
            "temp": round(self.temp, 2),
            "voltage": round(self.voltage, 2),
            "current": round(self.current, 2)
        }

# Cliente MQTT
mqtt_connected = False
mqtt_client = None

def on_connect(client, userdata, flags, rc):
    global mqtt_connected
    if rc == 0:
        print(f"✓ MQTT conectado ao broker {MQTT_BROKER}:{MQTT_PORT}")
        mqtt_connected = True
        
        # Subscreve nos tópicos de confirmação e resposta
        client.subscribe(f"iot/confirm/{DEVICE_ID}")
        client.subscribe(f"iot/response/{DEVICE_ID}")
        print(f"✓ Subscrito em: iot/confirm/{DEVICE_ID} e iot/response/{DEVICE_ID}")
    else:
        print(f"✗ Falha na conexão MQTT, código: {rc}")
        mqtt_connected = False

def on_message(client, userdata, msg):
    """Callback quando recebe mensagem MQTT"""
    print("\n" + "="*60)
    print(f"[MQTT RECEBIDO] Tópico: {msg.topic}")
    print(f"[MQTT RECEBIDO] Mensagem: {msg.payload.decode('utf-8')}")
    print("="*60 + "\n")

def on_disconnect(client, userdata, rc):
    global mqtt_connected
    mqtt_connected = False
    if rc != 0:
        print(f"✗ MQTT desconectado inesperadamente. Código: {rc}")

def register_device_mqtt():
    """Registra o dispositivo via MQTT enviando seu IP"""
    if not mqtt_connected:
        print("✗ MQTT não conectado, pulando registro")
        return False
    
    # Simula um IP local
    simulated_ip = "192.168.1.100"
    
    register_msg = {
        "device_id": DEVICE_ID,
        "ip": simulated_ip
    }
    
    payload = json.dumps(register_msg)
    result = mqtt_client.publish(MQTT_TOPIC, payload)
    
    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print(f"✓ Dispositivo registrado via MQTT: {payload}")
        return True
    else:
        print(f"✗ Falha ao publicar registro MQTT")
        return False

def send_sensor_data_mqtt(sensor_data):
    """Envia dados dos sensores via MQTT"""
    if not mqtt_connected:
        print("✗ MQTT não conectado, pulando envio de dados")
        return False
    
    mqtt_msg = {
        "device_id": DEVICE_ID,
        "sensor": "motor",
        "data": sensor_data,
        "timestamp": datetime.now().isoformat()
    }
    
    payload = json.dumps(mqtt_msg)
    topic = f"iot/sensor/{DEVICE_ID}"
    result = mqtt_client.publish(topic, payload)
    
    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print(f"✓ [MQTT] Dados enviados: {sensor_data}")
        return True
    else:
        print(f"✗ [MQTT] Falha ao enviar dados")
        return False

def send_sensor_data_http(sensor_data):
    """Envia dados dos sensores via HTTP POST"""
    url = f"http://{API_HOST}:{API_PORT}/esp/ingest"
    
    payload = {
        "device": DEVICE_ID,
        "sensor": "motor",
        "data": sensor_data,
        "ts": time.time() * 1000,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(
            url, 
            json=payload, 
            timeout=5,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print(f"✓ [HTTP] Dados enviados: {sensor_data}")
            return True
        else:
            print(f"✗ [HTTP] Erro {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ [HTTP] Falha na conexão: {e}")
        return False

def get_status_http():
    """Consulta status via HTTP GET (simulando a própria ESP expondo /status)"""
    # Nota: Este endpoint simula a ESP32 servindo dados, não o servidor API
    print("\n[INFO] Normalmente a ESP32 serve um endpoint /status local.")
    print("[INFO] Aqui estamos simulando apenas o envio de dados.\n")

def main():
    global mqtt_client
    
    print("="*60)
    print("SIMULADOR ESP32 - Enviando dados via MQTT e HTTP")
    print("="*60)
    print(f"Device ID: {DEVICE_ID}")
    print(f"API: http://{API_HOST}:{API_PORT}")
    print(f"MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print("="*60 + "\n")
    
    # Inicializa simulador de sensores
    sensors = SensorSimulator()
    
    # Configura cliente MQTT
    mqtt_client = mqtt.Client(client_id=DEVICE_ID)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.on_disconnect = on_disconnect
    
    # Conecta ao broker MQTT
    print(f"Conectando ao broker MQTT {MQTT_BROKER}:{MQTT_PORT}...")
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        mqtt_client.loop_start()  # Inicia loop em thread separada
    except Exception as e:
        print(f"✗ Erro ao conectar MQTT: {e}")
        print("Continuando apenas com HTTP...\n")
    
    # Aguarda conexão MQTT
    time.sleep(2)
    
    # Registra dispositivo via MQTT
    if mqtt_connected:
        register_device_mqtt()
        time.sleep(1)
    
    print("\nIniciando envio periódico de dados...")
    print("Pressione Ctrl+C para parar\n")
    
    cycle = 0
    try:
        while True:
            cycle += 1
            print(f"\n--- Ciclo {cycle} [{datetime.now().strftime('%H:%M:%S')}] ---")
            
            # Atualiza sensores
            sensors.update()
            sensor_data = sensors.get_data()
            
            # Envia via MQTT
            if mqtt_connected:
                send_sensor_data_mqtt(sensor_data)
            
            # A cada 2 ciclos, também envia via HTTP
            if cycle % 2 == 0:
                send_sensor_data_http(sensor_data)
            
            # Aguarda 5 segundos antes do próximo envio
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\n✓ Simulação interrompida pelo usuário")
    finally:
        if mqtt_client:
            mqtt_client.loop_stop()
            mqtt_client.disconnect()
        print("✓ Conexões encerradas")

if __name__ == "__main__":
    main()
