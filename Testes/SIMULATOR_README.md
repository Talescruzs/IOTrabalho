# Simulador ESP32

Este script Python simula o comportamento da ESP32 enviando dados de sensores para o servidor via MQTT e HTTP.

## 📋 Requisitos

Instale as dependências necessárias:

```bash
pip install paho-mqtt requests python-dotenv
```

Ou use o arquivo de requisitos da API:

```bash
pip install -r API/requirements.txt
```

## 🚀 Como Usar

### 1. Configure o arquivo .env

Certifique-se de que o arquivo `.env` está configurado corretamente:

```env
MQTT_BROKER=localhost
MQTT_PORT=1883
API_HOST=localhost
API_PORT=5000
```

### 2. Inicie o servidor API

Em um terminal, inicie o servidor Flask:

```bash
cd API
python Server.py
```

### 3. Inicie o broker MQTT (Mosquitto)

Se ainda não estiver rodando:

```bash
# No Linux/Ubuntu
sudo systemctl start mosquitto

# Ou rode manualmente
mosquitto -v
```

### 4. Execute o simulador

Em outro terminal:

```bash
python simulate_esp32.py
```

## 📊 O que o Simulador Faz

1. **Conecta ao broker MQTT** configurado no `.env`
2. **Registra o dispositivo** enviando seu ID e IP via MQTT no tópico `iot/register`
3. **Subscreve nos tópicos** de confirmação e resposta:
   - `iot/confirm/esp32-simulator`
   - `iot/response/esp32-simulator`
4. **Envia dados de sensores** periodicamente (a cada 5 segundos):
   - Via **MQTT** no tópico `iot/sensor/esp32-simulator`
   - Via **HTTP POST** para `/esp/ingest` (a cada 2 ciclos)

## 🔧 Dados Simulados

O simulador gera dados aleatórios para os seguintes sensores:

- **RPM**: 0 a 4000 (motor)
- **Temperatura**: 15°C a 45°C
- **Voltagem**: ~12V (±0.5V)
- **Corrente**: ~2.5A (±0.3A)

## 📝 Exemplo de Saída

```
=============================================================
SIMULADOR ESP32 - Enviando dados via MQTT e HTTP
=============================================================
Device ID: esp32-simulator
API: http://localhost:5000
MQTT Broker: localhost:1883
=============================================================

✓ MQTT conectado ao broker localhost:1883
✓ Subscrito em: iot/confirm/esp32-simulator e iot/response/esp32-simulator
✓ Dispositivo registrado via MQTT: {"device_id": "esp32-simulator", "ip": "192.168.1.100"}

--- Ciclo 1 [14:30:15] ---
✓ [MQTT] Dados enviados: {'rpm': 1045.23, 'temp': 26.5, 'voltage': 12.3, 'current': 2.6}

--- Ciclo 2 [14:30:20] ---
✓ [MQTT] Dados enviados: {'rpm': 1120.45, 'temp': 27.2, 'voltage': 12.1, 'current': 2.4}
✓ [HTTP] Dados enviados: {'rpm': 1120.45, 'temp': 27.2, 'voltage': 12.1, 'current': 2.4}
```

## 🔍 Verificando os Dados

### Via API HTTP

Consulte o último payload recebido:

```bash
curl http://localhost:5000/esp/latest
```

### Via MQTT (monitorar tópicos)

Em outro terminal:

```bash
mosquitto_sub -h localhost -t "iot/#" -v
```

## 🛑 Parar o Simulador

Pressione `Ctrl+C` no terminal onde o simulador está rodando.

## 🐛 Troubleshooting

### MQTT não conecta

- Verifique se o Mosquitto está rodando: `sudo systemctl status mosquitto`
- Verifique o IP/porta no `.env`
- Teste conexão manual: `mosquitto_sub -h localhost -t "test"`

### HTTP não envia

- Verifique se a API está rodando: `curl http://localhost:5000/`
- Verifique logs do servidor Flask
- Confirme que o firewall não está bloqueando a porta 5000

### Erro de importação

Instale as dependências:
```bash
pip install paho-mqtt requests python-dotenv
```
