#!/usr/bin/env python3
"""
Simulador de Laboratório IoT
Simula 4 ESPs controlando acesso, monitoramento ambiental e feedback visual
"""

import time
import json
import random
import requests
import paho.mqtt.client as mqtt
from datetime import datetime
import os
from pathlib import Path
import threading

# Carrega variáveis de ambiente
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent / '.env'
    load_dotenv(dotenv_path=env_path)
    print(f"✓ Variáveis carregadas de {env_path}")
except ImportError:
    print("AVISO: python-dotenv não instalado")

# Configurações
API_HOST = os.environ.get('API_HOST', 'localhost')
API_PORT = os.environ.get('API_PORT', '5000')
MQTT_BROKER = os.environ.get('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.environ.get('MQTT_PORT', 1883))

# Estado compartilhado do sistema
class LabState:
    def __init__(self):
        self.access_granted = False
        self.door_open = False
        self.temperature = 22.0
        self.humidity = 55.0
        self.alert_level = 0  # 0=OK (verde), 1=Aviso (amarelo), 2=Erro (vermelho)
        self.last_password_attempt = None
        self.lock = threading.Lock()

lab_state = LabState()

# ========== ESP1 - Teclado Matricial + Motor Vibração ==========
class ESP1_KeypadVibration:
    def __init__(self):
        self.device_id = "esp32-keypad"
        self.correct_password = "1234"
        self.mqtt_client = None
        self.connected = False
        
    def setup_mqtt(self):
        """Configura cliente MQTT"""
        self.mqtt_client = mqtt.Client(client_id=self.device_id)
        self.mqtt_client.on_connect = lambda c, u, f, rc: self._on_connect(rc)
        self.mqtt_client.on_disconnect = lambda c, u, rc: self._on_disconnect(rc)
        
        try:
            self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
            self.mqtt_client.loop_start()
            time.sleep(1)
        except Exception as e:
            print(f"[ESP1] ✗ Erro ao conectar MQTT: {e}")
    
    def _on_connect(self, rc):
        if rc == 0:
            self.connected = True
            print(f"[ESP1] ✓ MQTT conectado")
        else:
            print(f"[ESP1] ✗ Falha MQTT: {rc}")
    
    def _on_disconnect(self, rc):
        self.connected = False
        if rc != 0:
            print(f"[ESP1] ✗ MQTT desconectado: {rc}")
    
    def simulate_password_entry(self):
        """Simula entrada de senha pelo teclado"""
        # 70% chance de senha correta, 30% incorreta
        if random.random() < 0.7:
            password = self.correct_password
            vibration_pattern = "short"  # Vibração curta = autorizado
            with lab_state.lock:
                lab_state.access_granted = True
                lab_state.alert_level = 0  # Verde
        else:
            password = str(random.randint(1000, 9999))
            vibration_pattern = "long_x3"  # Vibração longa tripla = negado
            with lab_state.lock:
                lab_state.access_granted = False
                lab_state.alert_level = 2  # Vermelho
        
        with lab_state.lock:
            lab_state.last_password_attempt = password
        
        return password, vibration_pattern
    
    def send_data(self):
        """Envia dados do teclado e motor de vibração"""
        password, vibration = self.simulate_password_entry()
        
        data = {
            "password_length": len(password),
            "authorized": 1 if password == self.correct_password else 0,
            "vibration_duration": 200 if vibration == "short" else 600,
            "attempts": random.randint(1, 3)
        }
        
        # MQTT
        if self.connected:
            mqtt_msg = {
                "device_id": self.device_id,
                "sensor": "Teclado 4x4",
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
            self.mqtt_client.publish(f"iot/sensor/{self.device_id}", json.dumps(mqtt_msg))
            print(f"[ESP1] 🔐 Senha: {'✓ AUTORIZADA' if data['authorized'] else '✗ NEGADA'} - Vibração: {vibration}")
        
        # HTTP
        try:
            payload = {
                "device": self.device_id,
                "sensor": "Teclado 4x4",
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
            requests.post(f"http://{API_HOST}:{API_PORT}/esp/ingest", json=payload, timeout=5)
        except:
            pass
    
    def run(self):
        """Loop principal da ESP1"""
        self.setup_mqtt()
        
        # Registra ESP
        if self.connected:
            register_msg = {"device_id": self.device_id, "ip": "192.168.1.101"}
            self.mqtt_client.publish("iot/register", json.dumps(register_msg))
        
        while True:
            self.send_data()
            time.sleep(random.randint(8, 15))  # Tentativas de acesso a cada 8-15s

# ========== ESP2 - Módulo Relé + Encoder ==========
class ESP2_RelayEncoder:
    def __init__(self):
        self.device_id = "esp32-door"
        self.mqtt_client = None
        self.connected = False
        
    def setup_mqtt(self):
        """Configura cliente MQTT"""
        self.mqtt_client = mqtt.Client(client_id=self.device_id)
        self.mqtt_client.on_connect = lambda c, u, f, rc: self._on_connect(rc)
        self.mqtt_client.on_disconnect = lambda c, u, rc: self._on_disconnect(rc)
        
        try:
            self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
            self.mqtt_client.loop_start()
            time.sleep(1)
        except Exception as e:
            print(f"[ESP2] ✗ Erro ao conectar MQTT: {e}")
    
    def _on_connect(self, rc):
        if rc == 0:
            self.connected = True
            print(f"[ESP2] ✓ MQTT conectado")
        else:
            print(f"[ESP2] ✗ Falha MQTT: {rc}")
    
    def _on_disconnect(self, rc):
        self.connected = False
        if rc != 0:
            print(f"[ESP2] ✗ MQTT desconectado: {rc}")
    
    def send_data(self):
        """Envia dados do relé e encoder da porta"""
        with lab_state.lock:
            # Relé controla trava: 1=travado, 0=destravado
            relay_state = 0 if lab_state.access_granted else 1
            
            # Se acesso foi concedido, simula abertura da porta
            if lab_state.access_granted and random.random() < 0.8:
                lab_state.door_open = True
                encoder_position = random.randint(45, 90)  # Graus de abertura
            else:
                lab_state.door_open = False
                encoder_position = 0  # Porta fechada
        
        data = {
            "relay": relay_state,
            "door_angle": encoder_position,
            "door_open": 1 if encoder_position > 10 else 0,
            "lock_cycles": random.randint(0, 100)
        }
        
        # MQTT
        if self.connected:
            mqtt_msg = {
                "device_id": self.device_id,
                "sensor": "Relé JQC3F",
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
            self.mqtt_client.publish(f"iot/sensor/{self.device_id}", json.dumps(mqtt_msg))
            
            status = "🔓 ABERTA" if data['door_open'] else "🔒 FECHADA"
            lock = "Destravada" if relay_state == 0 else "Travada"
            print(f"[ESP2] 🚪 Porta: {status} ({encoder_position}°) - Trava: {lock}")
        
        # HTTP
        try:
            payload = {
                "device": self.device_id,
                "sensor": "Relé JQC3F",
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
            requests.post(f"http://{API_HOST}:{API_PORT}/esp/ingest", json=payload, timeout=5)
        except:
            pass
    
    def run(self):
        """Loop principal da ESP2"""
        self.setup_mqtt()
        
        # Registra ESP
        if self.connected:
            register_msg = {"device_id": self.device_id, "ip": "192.168.1.102"}
            self.mqtt_client.publish("iot/register", json.dumps(register_msg))
        
        while True:
            self.send_data()
            time.sleep(5)  # Monitora porta a cada 5s

# ========== ESP3 - Sensor DHT11 (Temperatura e Umidade) ==========
class ESP3_TempHumidity:
    def __init__(self):
        self.device_id = "esp32-ambiente"
        self.mqtt_client = None
        self.connected = False
        
    def setup_mqtt(self):
        """Configura cliente MQTT"""
        self.mqtt_client = mqtt.Client(client_id=self.device_id)
        self.mqtt_client.on_connect = lambda c, u, f, rc: self._on_connect(rc)
        self.mqtt_client.on_disconnect = lambda c, u, rc: self._on_disconnect(rc)
        
        try:
            self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
            self.mqtt_client.loop_start()
            time.sleep(1)
        except Exception as e:
            print(f"[ESP3] ✗ Erro ao conectar MQTT: {e}")
    
    def _on_connect(self, rc):
        if rc == 0:
            self.connected = True
            print(f"[ESP3] ✓ MQTT conectado")
        else:
            print(f"[ESP3] ✗ Falha MQTT: {rc}")
    
    def _on_disconnect(self, rc):
        self.connected = False
        if rc != 0:
            print(f"[ESP3] ✗ MQTT desconectado: {rc}")
    
    def update_environment(self):
        """Atualiza valores ambientais com variação natural"""
        with lab_state.lock:
            # Temperatura varia entre 18-28°C
            lab_state.temperature += random.uniform(-0.5, 0.5)
            lab_state.temperature = max(18, min(28, lab_state.temperature))
            
            # Umidade varia entre 40-70%
            lab_state.humidity += random.uniform(-2, 2)
            lab_state.humidity = max(40, min(70, lab_state.humidity))
            
            # Alerta se temperatura ou umidade fora da faixa ideal
            if lab_state.temperature > 26 or lab_state.humidity > 65:
                if lab_state.alert_level < 1:
                    lab_state.alert_level = 1  # Amarelo
            elif lab_state.temperature < 20 or lab_state.humidity < 45:
                if lab_state.alert_level < 1:
                    lab_state.alert_level = 1  # Amarelo
            else:
                if lab_state.alert_level == 1:
                    lab_state.alert_level = 0  # Verde
            
            return lab_state.temperature, lab_state.humidity
    
    def send_data(self):
        """Envia dados de temperatura e umidade"""
        temp, hum = self.update_environment()
        
        data = {
            "temperatura": round(temp, 2),
            "umidade": round(hum, 2),
            "heat_index": round(temp + (hum * 0.1), 2),  # Índice de calor simplificado
            "dew_point": round(temp - ((100 - hum) / 5), 2)  # Ponto de orvalho aproximado
        }
        
        # MQTT
        if self.connected:
            mqtt_msg = {
                "device_id": self.device_id,
                "sensor": "DHT11",
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
            self.mqtt_client.publish(f"iot/sensor/{self.device_id}", json.dumps(mqtt_msg))
            print(f"[ESP3] 🌡️  {temp:.1f}°C | 💧 {hum:.1f}%")
        
        # HTTP
        try:
            payload = {
                "device": self.device_id,
                "sensor": "DHT11",
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
            requests.post(f"http://{API_HOST}:{API_PORT}/esp/ingest", json=payload, timeout=5)
        except:
            pass
    
    def run(self):
        """Loop principal da ESP3"""
        self.setup_mqtt()
        
        # Registra ESP
        if self.connected:
            register_msg = {"device_id": self.device_id, "ip": "192.168.1.103"}
            self.mqtt_client.publish("iot/register", json.dumps(register_msg))
        
        while True:
            self.send_data()
            time.sleep(10)  # Lê temperatura a cada 10s

# ========== ESP4 - 3 LEDs (Status Visual) ==========
class ESP4_StatusLEDs:
    def __init__(self):
        self.device_id = "esp32-leds"
        self.mqtt_client = None
        self.connected = False
        
    def setup_mqtt(self):
        """Configura cliente MQTT"""
        self.mqtt_client = mqtt.Client(client_id=self.device_id)
        self.mqtt_client.on_connect = lambda c, u, f, rc: self._on_connect(rc)
        self.mqtt_client.on_disconnect = lambda c, u, rc: self._on_disconnect(rc)
        
        try:
            self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
            self.mqtt_client.loop_start()
            time.sleep(1)
        except Exception as e:
            print(f"[ESP4] ✗ Erro ao conectar MQTT: {e}")
    
    def _on_connect(self, rc):
        if rc == 0:
            self.connected = True
            print(f"[ESP4] ✓ MQTT conectado")
        else:
            print(f"[ESP4] ✗ Falha MQTT: {rc}")
    
    def _on_disconnect(self, rc):
        self.connected = False
        if rc != 0:
            print(f"[ESP4] ✗ MQTT desconectado: {rc}")
    
    def send_data(self):
        """Envia estado dos LEDs baseado no estado do laboratório"""
        with lab_state.lock:
            alert = lab_state.alert_level
        
        # Apenas um LED aceso por vez
        if alert == 0:  # Tudo OK
            led_green = 255
            led_yellow = 0
            led_red = 0
            status_text = "✅ NORMAL"
        elif alert == 1:  # Aviso
            led_green = 0
            led_yellow = 255
            led_red = 0
            status_text = "⚠️ ALERTA"
        else:  # Erro/Negado
            led_green = 0
            led_yellow = 0
            led_red = 255
            status_text = "🚨 ERRO"
        
        data = {
            "led_green": led_green,
            "led_yellow": led_yellow,
            "led_red": led_red,
            "brightness": random.randint(200, 255)
        }
        
        # MQTT
        if self.connected:
            mqtt_msg = {
                "device_id": self.device_id,
                "sensor": "KY023",
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
            self.mqtt_client.publish(f"iot/sensor/{self.device_id}", json.dumps(mqtt_msg))
            print(f"[ESP4] 💡 Status: {status_text}")
        
        # HTTP
        try:
            payload = {
                "device": self.device_id,
                "sensor": "KY023",
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
            requests.post(f"http://{API_HOST}:{API_PORT}/esp/ingest", json=payload, timeout=5)
        except:
            pass
    
    def run(self):
        """Loop principal da ESP4"""
        self.setup_mqtt()
        
        # Registra ESP
        if self.connected:
            register_msg = {"device_id": self.device_id, "ip": "192.168.1.104"}
            self.mqtt_client.publish("iot/register", json.dumps(register_msg))
        
        while True:
            self.send_data()
            time.sleep(3)  # Atualiza LEDs a cada 3s

# ========== MAIN ==========
def print_banner():
    print("\n" + "="*70)
    print("🏢 SIMULADOR DE LABORATÓRIO IoT")
    print("="*70)
    print("ESP1 (192.168.1.101) - Teclado Matricial + Motor Vibração")
    print("ESP2 (192.168.1.102) - Relé + Encoder (Controle de Porta)")
    print("ESP3 (192.168.1.103) - DHT11 (Temperatura e Umidade)")
    print("ESP4 (192.168.1.104) - 3 LEDs (Status Visual)")
    print("="*70)
    print(f"API: http://{API_HOST}:{API_PORT}")
    print(f"MQTT: {MQTT_BROKER}:{MQTT_PORT}")
    print("="*70 + "\n")

def main():
    print_banner()
    
    # Cria instâncias das ESPs
    esp1 = ESP1_KeypadVibration()
    esp2 = ESP2_RelayEncoder()
    esp3 = ESP3_TempHumidity()
    esp4 = ESP4_StatusLEDs()
    
    # Cria threads para cada ESP
    threads = [
        threading.Thread(target=esp1.run, daemon=True, name="ESP1-Keypad"),
        threading.Thread(target=esp2.run, daemon=True, name="ESP2-Door"),
        threading.Thread(target=esp3.run, daemon=True, name="ESP3-TempHum"),
        threading.Thread(target=esp4.run, daemon=True, name="ESP4-LEDs")
    ]
    
    # Inicia todas as threads
    print("🚀 Iniciando simulação de todas as ESPs...\n")
    for thread in threads:
        thread.start()
        time.sleep(0.5)  # Pequeno delay entre inicializações
    
    print("✓ Todas as ESPs estão rodando!")
    print("Pressione Ctrl+C para parar\n")
    
    try:
        # Mantém o programa rodando
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n✓ Simulação interrompida pelo usuário")
        print("✓ Encerrando todas as ESPs...")

if __name__ == "__main__":
    main()
