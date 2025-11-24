#!/usr/bin/env python3
"""
Simulador ESP32_DOOR - Sensor de Porta com Encoder
Simula o comportamento da ESP32 que monitora a porta e controla o relé
"""

import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================
MQTT_BROKER = "192.168.143.117"  # Ajuste para o IP do seu broker
MQTT_PORT = 1883
DEVICE_ID = "ESP32_DOOR"
DEVICE_IP = "192.168.1.100"  # IP simulado

# Tópicos MQTT
TOPIC_REGISTER = "iot/register"
TOPIC_SENSOR = f"iot/sensor/{DEVICE_ID}"
TOPIC_RESPONSE = f"iot/response/{DEVICE_ID}"
TOPIC_CONFIRM = f"iot/confirm/{DEVICE_ID}"

# Estado simulado
porta_aberta = False
porta_desbloqueada = False
tempo_abertura = None

# ============================================================================
# CALLBACKS MQTT
# ============================================================================

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✓ Conectado ao broker MQTT")
        print(f"✓ Subscrevendo em: {TOPIC_RESPONSE}")
        print(f"✓ Subscrevendo em: {TOPIC_CONFIRM}")
        
        # Subscreve nos tópicos de resposta
        client.subscribe(TOPIC_RESPONSE)
        client.subscribe(TOPIC_CONFIRM)
        
        # Registra o dispositivo
        registrar_dispositivo(client)
    else:
        print(f"✗ Falha na conexão MQTT. Código: {rc}")

def on_message(client, userdata, msg):
    global porta_desbloqueada
    
    print(f"\n>>> Mensagem recebida [{msg.topic}]")
    try:
        payload = json.loads(msg.payload.decode())
        print(f"    Payload: {json.dumps(payload, indent=2)}")
        
        # Processa comandos
        if "command" in payload:
            command = payload.get("command")
            params = payload.get("params", {})
            
            print(f"\n{'='*60}")
            print(f"COMANDO RECEBIDO: {command}")
            print(f"Parâmetros: {params}")
            print(f"{'='*60}")
            
            if command == "destravar":
                destravar = params.get("destravar", False)
                if destravar:
                    porta_desbloqueada = True
                    print("🔓 PORTA DESTRAVADA - Relé ativado")
                else:
                    porta_desbloqueada = False
                    print("🔒 PORTA TRAVADA - Relé desativado")
                    
            elif command == "unlock_door":
                porta_desbloqueada = True
                print("🔓 PORTA DESTRAVADA - Relé ativado")
                
            elif command == "lock_door":
                porta_desbloqueada = False
                print("🔒 PORTA TRAVADA - Relé desativado")
            
            print(f"{'='*60}\n")
            
    except json.JSONDecodeError:
        print(f"    Conteúdo: {msg.payload.decode()}")

# ============================================================================
# FUNÇÕES DE ENVIO
# ============================================================================

def registrar_dispositivo(client):
    """Registra o dispositivo no servidor"""
    dados = {
        "device_id": DEVICE_ID,
        "ip": DEVICE_IP
    }
    
    payload = json.dumps(dados)
    result = client.publish(TOPIC_REGISTER, payload)
    
    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print(f"\n✓ Dispositivo registrado: {DEVICE_ID}")
        print(f"  IP: {DEVICE_IP}")
    else:
        print(f"\n✗ Falha ao registrar dispositivo")

def enviar_dados_porta(client, aberta, alerta=False):
    """Envia dados do sensor de porta"""
    dados = {
        "device_id": DEVICE_ID,
        "sensor": "encoder",
        "data": {
            "porta_aberta": aberta,
            "alerta": alerta
        },
        "timestamp": str(int(time.time() * 1000))
    }
    
    payload = json.dumps(dados)
    result = client.publish(TOPIC_SENSOR, payload)
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    status = "ABERTA" if aberta else "FECHADA"
    alerta_str = " [ALERTA!]" if alerta else ""
    
    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print(f"\n[{timestamp}] 📤 Dados enviados:")
        print(f"  🚪 Porta: {status}{alerta_str}")
        print(f"  Payload: {payload}")
    else:
        print(f"\n✗ Falha ao enviar dados")

# ============================================================================
# MENU INTERATIVO
# ============================================================================

def mostrar_menu():
    print("\n" + "="*60)
    print("SIMULADOR ESP32_DOOR - Controle de Porta")
    print("="*60)
    print(f"Estado atual:")
    print(f"  🚪 Porta: {'ABERTA' if porta_aberta else 'FECHADA'}")
    print(f"  🔐 Relé: {'DESTRAVADO' if porta_desbloqueada else 'TRAVADO'}")
    print("\nOpções:")
    print("  [1] Abrir porta")
    print("  [2] Fechar porta")
    print("  [3] Simular alerta de timeout")
    print("  [4] Modo automático (teste completo)")
    print("  [5] Registrar dispositivo novamente")
    print("  [0] Sair")
    print("="*60)

def modo_automatico(client):
    """Simula sequência automática de eventos"""
    global porta_aberta, porta_desbloqueada, tempo_abertura
    
    print("\n🤖 Iniciando modo automático...")
    print("Aguarde, simulando cenário completo...\n")
    
    # 1. Porta abre
    print("\n[Cenário 1] Porta abrindo...")
    time.sleep(2)
    porta_aberta = True
    tempo_abertura = time.time()
    enviar_dados_porta(client, True, False)
    time.sleep(3)
    
    # 2. Porta fecha rapidamente (sem alerta)
    print("\n[Cenário 2] Porta fechando normalmente...")
    time.sleep(2)
    porta_aberta = False
    tempo_abertura = None
    porta_desbloqueada = False  # Trava automaticamente
    enviar_dados_porta(client, False, False)
    time.sleep(3)
    
    # 3. Porta abre novamente e fica aberta por muito tempo
    print("\n[Cenário 3] Porta abrindo e ficando aberta...")
    time.sleep(2)
    porta_aberta = True
    tempo_abertura = time.time()
    enviar_dados_porta(client, True, False)
    
    # Aguarda 6 segundos (simula timeout)
    for i in range(6):
        time.sleep(1)
        print(f"  ⏱️  Porta aberta há {i+1} segundos...")
    
    # 4. Envia alerta de timeout
    print("\n[Cenário 4] ⚠️  TIMEOUT! Porta aberta por muito tempo!")
    enviar_dados_porta(client, True, True)
    time.sleep(3)
    
    # 5. Porta finalmente fecha
    print("\n[Cenário 5] Porta fechando após alerta...")
    time.sleep(2)
    porta_aberta = False
    tempo_abertura = None
    porta_desbloqueada = False
    enviar_dados_porta(client, False, False)
    
    print("\n✓ Modo automático concluído!")

# ============================================================================
# MAIN
# ============================================================================

def main():
    global porta_aberta, porta_desbloqueada, tempo_abertura
    
    print("\n" + "="*60)
    print("SIMULADOR ESP32_DOOR")
    print("="*60)
    print(f"Device ID: {DEVICE_ID}")
    print(f"MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"IP Simulado: {DEVICE_IP}")
    print("="*60)
    
    # Configurar cliente MQTT
    client = mqtt.Client(client_id=DEVICE_ID)
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        print(f"\nConectando ao broker MQTT...")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        
        # Aguarda conexão
        time.sleep(2)
        
        # Loop do menu
        while True:
            mostrar_menu()
            opcao = input("\nEscolha uma opção: ").strip()
            
            if opcao == "1":
                # Abrir porta
                if not porta_aberta:
                    porta_aberta = True
                    tempo_abertura = time.time()
                    enviar_dados_porta(client, True, False)
                else:
                    print("⚠️  Porta já está aberta!")
                    
            elif opcao == "2":
                # Fechar porta
                if porta_aberta:
                    porta_aberta = False
                    tempo_abertura = None
                    porta_desbloqueada = False  # Trava automaticamente ao fechar
                    enviar_dados_porta(client, False, False)
                else:
                    print("⚠️  Porta já está fechada!")
                    
            elif opcao == "3":
                # Alerta de timeout
                if porta_aberta:
                    enviar_dados_porta(client, True, True)
                else:
                    print("⚠️  Porta precisa estar aberta para enviar alerta!")
                    
            elif opcao == "4":
                # Modo automático
                modo_automatico(client)
                
            elif opcao == "5":
                # Registrar novamente
                registrar_dispositivo(client)
                
            elif opcao == "0":
                # Sair
                print("\n👋 Encerrando simulador...")
                break
                
            else:
                print("❌ Opção inválida!")
            
            time.sleep(0.5)
    
    except KeyboardInterrupt:
        print("\n\n👋 Simulador interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.loop_stop()
        client.disconnect()
        print("✓ Desconectado do broker MQTT")

if __name__ == "__main__":
    main()
