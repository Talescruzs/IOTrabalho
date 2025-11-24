"""
Sistema de Controle de Acesso - Lógica de Processamento
Gerencia a comunicação entre as 4 ESPs do sistema de controle de acesso
"""

import requests
import json
import time
from datetime import datetime
from threading import Thread, Lock

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================
SENHA_CORRETA = "1234"
TEMP_LIMITE = 30.0
TIMEOUT_PORTA_ABERTA = 5  # segundos

# IPs das ESPs (serão atualizados dinamicamente)
ESP_IPS = {
    "ESP32_KEYPAD": None,    # ESP1
    "ESP32_DOOR": None,       # ESP2
    "ESP32_CLIMATE": None,    # ESP3
    "ESP32_LEDS": None        # ESP4
}

# Estado do sistema
system_state = {
    "porta_desbloqueada": False,
    "porta_aberta": False,
    "tempo_abertura": None,
    "temperatura_alta": False,
    "ultima_tentativa": None,
    "lock": Lock()
}

# ============================================================================
# FUNÇÕES DE COMUNICAÇÃO COM ESPs
# ============================================================================

def send_command_http(device_id, command, params=None):
    """Envia comando para ESP via HTTP POST"""
    ip = ESP_IPS.get(device_id)
    if not ip:
        print(f"[access_control] ⚠ IP não encontrado para {device_id}", flush=True)
        return False
    
    url = f"http://{ip}/command"
    payload = {
        "command": command,
        "params": params or {}
    }
    
    try:
        response = requests.post(url, json=payload, timeout=3)
        if response.status_code == 200:
            print(f"[access_control] ✓ Comando '{command}' enviado para {device_id}", flush=True)
            return True
        else:
            print(f"[access_control] ✗ Erro ao enviar comando para {device_id}: {response.status_code}", flush=True)
            return False
    except requests.exceptions.RequestException as e:
        print(f"[access_control] ✗ Falha na conexão com {device_id}: {e}", flush=True)
        return False

def send_command_mqtt(mqtt_client, device_id, command, params=None):
    """Envia comando para ESP via MQTT"""
    if not mqtt_client:
        print(f"[access_control] ⚠ Cliente MQTT não disponível", flush=True)
        return False
    
    topic = f"iot/response/{device_id}"
    payload = {
        "command": command,
        "params": params or {}
    }
    
    try:
        result = mqtt_client.publish(topic, json.dumps(payload))
        if result.rc == 0:
            print(f"[access_control] ✓ Comando MQTT '{command}' enviado para {device_id}", flush=True)
            return True
        else:
            print(f"[access_control] ✗ Erro ao publicar MQTT para {device_id}", flush=True)
            return False
    except Exception as e:
        print(f"[access_control] ✗ Erro MQTT: {e}", flush=True)
        return False

def update_esp_ip(device_id, ip):
    """Atualiza IP de uma ESP"""
    ESP_IPS[device_id] = ip
    print(f"[access_control] ✓ IP atualizado: {device_id} = {ip}", flush=True)

# ============================================================================
# LÓGICA DE CONTROLE DE ACESSO
# ============================================================================

def process_access_attempt(data, mqtt_client=None):
    """
    Processa tentativa de acesso do teclado (ESP1)
    
    Formato esperado:
    {
        "device_id": "ESP32_KEYPAD",
        "sensor": "access_attempt",
        "data": {
            "password": "1234",
            "authorized": 1,
            "length": 4
        }
    }
    """
    print("\n" + "="*60, flush=True)
    print("[ACESSO] Tentativa de acesso detectada", flush=True)
    print("="*60, flush=True)
    
    password = data.get("password", "")
    authorized = data.get("authorized", 0)
    
    with system_state["lock"]:
        system_state["ultima_tentativa"] = {
            "timestamp": datetime.now().isoformat(),
            "password": password,
            "authorized": authorized
        }
    
    if authorized == 1:
        print(f"[ACESSO] ✓ AUTORIZADO - Senha: {password}", flush=True)
        
        # ESP1: Vibração curta (1s)
        send_command_http("ESP32_KEYPAD", "vibrate_short")
        send_command_mqtt(mqtt_client, "ESP32_KEYPAD", "vibrate_short")
        
        # ESP4: LED verde (3s)
        send_command_http("ESP32_LEDS", "pisca", {"pisca": 2})
        # send_command_mqtt(mqtt_client, "ESP32_LEDS", "led_green", {"duration": 3000})
        
        # ESP2: Desbloqueia porta
        send_command_http("ESP32_DOOR", {"destravar": True})
        # send_command_mqtt(mqtt_client, "ESP32_DOOR", "unlock_door")
        
        with system_state["lock"]:
            system_state["porta_desbloqueada"] = True
        
        print("[ACESSO] ✓ Comandos de acesso autorizado enviados", flush=True)
        
    else:
        print(f"[ACESSO] ✗ NEGADO - Senha: {password}", flush=True)
        
        # ESP1: Vibração longa (3s)
        send_command_http("ESP32_KEYPAD", "vibrate_long")
        send_command_mqtt(mqtt_client, "ESP32_KEYPAD", "vibrate_long")
        
        # ESP4: LED vermelho (3s)
        send_command_http("ESP32_LEDS", "pisca", {"pisca": 1})
        # send_command_mqtt(mqtt_client, "ESP32_LEDS", "led_red", {"duration": 3000})
        
        print("[ACESSO] ✓ Comandos de acesso negado enviados", flush=True)
    
    print("="*60 + "\n", flush=True)

def process_encoder(data, mqtt_client=None):
    """
    Processa dados do sensor de porta (ESP2)
    
    Formato esperado:
    {
        "device_id": "ESP32_DOOR",
        "sensor": "encoder",
        "data": {
            "alerta": true,
            "porta_aberta": true
        }
    }
    """
    porta_aberta = data.get("porta_aberta", False)
    alerta = data.get("alerta", False)
    
    with system_state["lock"]:
        porta_estava_aberta = system_state["porta_aberta"]
        system_state["porta_aberta"] = porta_aberta
        
        if porta_aberta and not porta_estava_aberta:
            # Porta acabou de abrir
            system_state["tempo_abertura"] = time.time()
            print(f"[PORTA] 🚪 Porta ABERTA", flush=True)
            
        elif not porta_aberta and porta_estava_aberta:
            # Porta acabou de fechar
            system_state["tempo_abertura"] = None
            print(f"[PORTA] 🚪 Porta FECHADA", flush=True)
            
            # ESP4: Apaga LEDs
            send_command_http("ESP32_LEDS", "alerta", {"alerta": False})
            # send_command_mqtt(mqtt_client, "ESP32_LEDS", "led_off")
        
        # Processa alerta de timeout
        if alerta:
            print(f"[PORTA] ⚠️  ALERTA: Porta aberta por muito tempo!", flush=True)
            
            # ESP4: Acende LEDs verde + vermelho (alerta)
            send_command_http("ESP32_LEDS", "alerta", {"alerta": True})
            # send_command_mqtt(mqtt_client, "ESP32_LEDS", "led_alert")

def process_door_alert(data, mqtt_client=None):
    """
    Processa alerta de porta aberta por muito tempo (ESP2)
    
    Formato esperado:
    {
        "device_id": "ESP32_DOOR",
        "sensor": "alert",
        "data": {
            "alert": "door_open_timeout",
            "duration": 7
        }
    }
    """
    alert_type = data.get("alert", "")
    duration = data.get("duration", 0)
    
    if alert_type == "door_open_timeout":
        print(f"[PORTA] ⚠️  ALERTA: Porta aberta há {duration} segundos!", flush=True)
        
        # ESP4: Acende LEDs verde + vermelho (alerta)
        send_command_http("ESP32_LEDS", "alerta", {"alerta": True})
        # send_command_mqtt(mqtt_client, "ESP32_LEDS", "led_alert")

def process_climate(data, mqtt_client=None):
    """
    Processa dados ambientais (ESP3)
    
    Formato esperado:
    {
        "device_id": "ESP32_CLIMATE",
        "sensor": "climate",
        "data": {
            "temperature": 28.5,
            "humidity": 62.3,
            "temp_alert": 0
        }
    }
    """
    temperature = data.get("temperature", 0)
    humidity = data.get("humidity", 0)
    temp_alert = data.get("temp_alert", 0)
    
    with system_state["lock"]:
        estava_alta = system_state["temperatura_alta"]
        system_state["temperatura_alta"] = (temp_alert == 1)
        
        if temp_alert == 1 and not estava_alta:
            # Temperatura acabou de exceder o limite
            print(f"[CLIMA] ⚠️  ALERTA: Temperatura alta: {temperature}°C", flush=True)
            
            # ESP4: Acende LED amarelo
            send_command_http("ESP32_LEDS", "pisca", {"pisca": 3})  # 0 = fica aceso
            # send_command_mqtt(mqtt_client, "ESP32_LEDS", "led_yellow", {"duration": 0})
            
        elif temp_alert == 0 and not estava_alta:
            # Temperatura voltou ao normal
            print(f"[CLIMA] ✓ Temperatura normalizada: {temperature}°C", flush=True)
            
            # ESP4: Apaga LED amarelo
            send_command_http("ESP32_LEDS", "alerta", {"alerta": False})
            # send_command_mqtt(mqtt_client, "ESP32_LEDS", "led_off")

# ============================================================================
# PROCESSADOR PRINCIPAL
# ============================================================================

def process_sensor_data(device_id, sensor, data, mqtt_client=None):
    """
    Processa dados recebidos de qualquer ESP e dispara ações apropriadas
    
    Args:
        device_id: ID da ESP que enviou os dados
        sensor: Tipo de sensor/evento
        data: Dados do sensor
        mqtt_client: Cliente MQTT (opcional, para enviar comandos via MQTT)
    """
    try:
        if sensor == "access_attempt":
            process_access_attempt(data, mqtt_client)
            
        elif sensor == "encoder":
            process_encoder(data, mqtt_client)
            
        elif sensor == "alert":
            process_door_alert(data, mqtt_client)
            
        elif sensor == "climate":
            process_climate(data, mqtt_client)
            
        elif sensor == "led_status":
            # Status dos LEDs - apenas log
            print(f"[LEDS] Status: {data}", flush=True)
            
        elif sensor == "motor":
            # Processa dados do sensor motor (ESP32_LAB_001)
            temperature = data.get("temp", 0)
            
            print(f"[MOTOR] Temperatura: {temperature}°C", flush=True)
            
            # Verifica se temperatura > 25°C
            if temperature > 25:
                print(f"[MOTOR] ⚠️  Temperatura acima de 25°C! Enviando confirmação...", flush=True)
                
                # Envia {retorno: true} para ESP32_LAB_001
                send_command_http("ESP32_LAB_002", "retorno", {"retorno": True})
                send_command_mqtt(mqtt_client, "ESP32_LAB_002", "retorno", {"retorno": True})
            else:
                print(f"[MOTOR] ✓ Temperatura normal (< 25°C)", flush=True)
            
        else:
            print(f"[access_control] Sensor desconhecido: {sensor}", flush=True)
            
    except Exception as e:
        print(f"[access_control] ERRO ao processar dados: {e}", flush=True)
        import traceback
        traceback.print_exc()

def get_system_status():
    """Retorna status atual do sistema"""
    with system_state["lock"]:
        return {
            "porta_desbloqueada": system_state["porta_desbloqueada"],
            "porta_aberta": system_state["porta_aberta"],
            "temperatura_alta": system_state["temperatura_alta"],
            "tempo_porta_aberta": time.time() - system_state["tempo_abertura"] if system_state["tempo_abertura"] else 0,
            "ultima_tentativa": system_state["ultima_tentativa"],
            "esp_ips": ESP_IPS
        }
