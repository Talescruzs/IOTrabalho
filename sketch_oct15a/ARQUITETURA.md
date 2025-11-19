# Arquitetura da Classe Connection

## 📐 Diagrama de Classes

```
┌─────────────────────────────────────────────────────────────┐
│                     Connection                              │
├─────────────────────────────────────────────────────────────┤
│ - _ssid: const char*                                        │
│ - _password: const char*                                    │
│ - _deviceId: const char*                                    │
│ - _mqttBroker: const char*                                  │
│ - _mqttPort: uint16_t                                       │
│ - _ledPin: int                                              │
│ - _deviceIP: String                                         │
│ - _espClient: WiFiClient                                    │
│ - _mqttClient: PubSubClient                                 │
│ - _httpServer: WiFiServer                                   │
│ - _wifiConnected: bool                                      │
│ - _mqttConnected: bool                                      │
│ - _lastMqttReconnect: unsigned long                         │
│ - _lastSensorSend: unsigned long                            │
├─────────────────────────────────────────────────────────────┤
│ + Connection(ssid, password, deviceId, mqttBroker, ...)     │
│ + begin(): bool                                             │
│ + sendSensorData(sensor, data): bool                        │
│ + sendSensorData(sensor, keys[], vals[], count): bool       │
│ + sendHTTPPost(host, port, endpoint, payload): bool         │
│ + processHTTP(): void                                       │
│ + tick(): void                                              │
│ + isWiFiConnected(): bool                                   │
│ + isMQTTConnected(): bool                                   │
│ + getDeviceIP(): String                                     │
│ + getDeviceId(): String                                     │
│ - connectWiFi(): bool                                       │
│ - connectMQTT(): bool                                       │
│ - registerDevice(): void                                    │
│ - onMqttMessage(topic, payload, length): void               │
│ - sendJsonResponse(client, json): void                      │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Fluxo de Comunicação

```
┌──────────┐
│  ESP32   │
└────┬─────┘
     │
     │ 1. begin()
     ▼
┌─────────────────┐
│  connectWiFi()  │──────► WiFi.begin(ssid, password)
└────┬────────────┘
     │ ✓ WiFi OK
     │
     ▼
┌─────────────────┐
│  connectMQTT()  │──────► mqttClient.connect(deviceId)
└────┬────────────┘
     │ ✓ MQTT OK
     │
     ▼
┌──────────────────┐
│ registerDevice() │──────► publish("iot/register", {device_id, ip})
└────┬─────────────┘
     │ ✓ Registrado
     │
     │ 2. tick() [loop contínuo]
     ▼
┌─────────────────────────────────────────┐
│           Manutenção                     │
│  • mqttClient.loop()                    │
│  • Reconecta MQTT se desconectado       │
│  • processHTTP()                        │
└────┬────────────────────────────────────┘
     │
     │ 3. sendSensorData()
     ▼
┌──────────────────────────────────────────┐
│  Publica dados no MQTT                   │
│  Topic: iot/sensor/{deviceId}            │
│  Payload: {device_id, sensor, data, ts}  │
└──────────────────────────────────────────┘
```

## 📡 Fluxo de Mensagens MQTT

```
ESP32                           MQTT Broker                    Servidor Python
  │                                  │                               │
  │ 1. CONNECT                       │                               │
  ├─────────────────────────────────►│                               │
  │                                  │                               │
  │ 2. SUBSCRIBE                     │                               │
  │    iot/confirm/esp32             │                               │
  │    iot/response/esp32            │                               │
  ├─────────────────────────────────►│                               │
  │                                  │                               │
  │ 3. PUBLISH                       │                               │
  │    iot/register                  │                               │
  │    {device_id, ip}               │                               │
  ├─────────────────────────────────►│──────────────────────────────►│
  │                                  │         (mqtt_listener.py)    │
  │                                  │                               │
  │                                  │ 4. PUBLISH                    │
  │                                  │    iot/confirm/esp32          │
  │                                  │    {status: "registered"}     │
  │◄─────────────────────────────────┼───────────────────────────────┤
  │                                  │                               │
  │ 5. PUBLISH (periodicamente)      │                               │
  │    iot/sensor/esp32              │                               │
  │    {device_id, sensor, data}     │                               │
  ├─────────────────────────────────►│──────────────────────────────►│
  │                                  │         (salva no banco)      │
  │                                  │                               │
  │                                  │ 6. PUBLISH                    │
  │                                  │    iot/response/esp32         │
  │                                  │    {status: "received"}       │
  │◄─────────────────────────────────┼───────────────────────────────┤
  │                                  │                               │
  │ (LED pisca ao receber mensagem)  │                               │
  │                                  │                               │
```

## 🌐 Servidor HTTP Local

```
Cliente Web                      ESP32 (Connection)
    │                                 │
    │ GET /                           │
    ├────────────────────────────────►│
    │                                 │
    │ HTML com links                  │
    │◄────────────────────────────────┤
    │                                 │
    │ GET /H                          │
    ├────────────────────────────────►│
    │                                 │ digitalWrite(LED, HIGH)
    │ 200 OK                          │
    │◄────────────────────────────────┤
    │                                 │
    │ GET /status                     │
    ├────────────────────────────────►│
    │                                 │ Coleta dados dos sensores
    │ JSON                            │
    │ {device, sensor, data, ts}      │
    │◄────────────────────────────────┤
    │                                 │
```

## 🔌 Métodos de Envio de Dados

```
┌────────────────────────────────────────────────────────────┐
│              Métodos Disponíveis                           │
└────────────────────────────────────────────────────────────┘

1️⃣  sendSensorData(String sensor, JSONVar data)
    ├─ Uso: Dados complexos com múltiplos campos
    ├─ Exemplo: dados["rpm"] = 1500; dados["temp"] = 25.3;
    └─ Retorna: bool (true = sucesso)

2️⃣  sendSensorData(String sensor, char* keys[], double vals[], size_t count)
    ├─ Uso: Dados simples com arrays
    ├─ Exemplo: keys={"rpm","temp"}, vals={1500, 25.3}
    └─ Retorna: bool (true = sucesso)

3️⃣  sendHTTPPost(char* host, uint16_t port, String endpoint, String json)
    ├─ Uso: Enviar para servidor HTTP externo
    ├─ Exemplo: POST http://192.168.1.100:5000/api/data
    └─ Retorna: bool (true = sucesso)

4️⃣  processHTTP()
    ├─ Uso: Processa requisições do servidor HTTP local
    ├─ Endpoints: /, /H, /L, /status
    └─ Chamado automaticamente em tick()
```

## 🔧 Ciclo de Vida

```
┌─────────────────────────────────────────────────────────────┐
│                    CICLO DE VIDA                            │
└─────────────────────────────────────────────────────────────┘

SETUP (uma vez)
  │
  ├─► begin()
  │    ├─► Serial.begin(9600)
  │    ├─► pinMode(LED, OUTPUT)
  │    ├─► connectWiFi()
  │    │    └─► WiFi.begin(ssid, password)
  │    ├─► httpServer.begin()
  │    └─► connectMQTT()
  │         ├─► mqttClient.setServer()
  │         ├─► mqttClient.connect()
  │         ├─► mqttClient.subscribe()
  │         └─► registerDevice()
  │              └─► publish("iot/register")
  │
  └─► Retorna true/false

LOOP (contínuo)
  │
  ├─► tick()
  │    ├─► mqttClient.loop()
  │    ├─► Verifica reconexão MQTT (a cada 5s)
  │    └─► processHTTP()
  │
  ├─► sendSensorData() [quando chamado]
  │    ├─► Verifica se MQTT conectado
  │    ├─► Constrói mensagem JSON
  │    └─► mqttClient.publish()
  │
  └─► [Seu código]
       └─► Lê sensores, lógica de negócio, etc.
```

## 📦 Estrutura de Dados

### Mensagem de Registro
```json
{
  "device_id": "esp32",
  "ip": "192.168.1.100"
}
```
**Tópico:** `iot/register`

### Mensagem de Sensor
```json
{
  "device_id": "esp32",
  "sensor": "motor",
  "data": {
    "rpm": 1500.5,
    "temp": 25.3,
    "voltage": 12.1,
    "current": 2.5
  },
  "timestamp": "123456"
}
```
**Tópico:** `iot/sensor/{device_id}`

### Resposta HTTP /status
```json
{
  "device": "esp32",
  "sensor": "motor",
  "data": {
    "rpm": 1500.5,
    "temp": 25.3
  },
  "ts": 123456.0
}
```

## 🎯 Estados da Conexão

```
┌─────────────────────────────────────────────────────────────┐
│                   ESTADOS POSSÍVEIS                         │
└─────────────────────────────────────────────────────────────┘

Estado 1: Desconectado Total
  WiFi: ✗  MQTT: ✗
  └─► Tenta conectar WiFi no begin()

Estado 2: Apenas WiFi
  WiFi: ✓  MQTT: ✗
  └─► Tenta conectar MQTT no begin()
  └─► Reconecta automaticamente a cada 5s no tick()

Estado 3: Tudo Conectado
  WiFi: ✓  MQTT: ✓
  └─► Pode enviar dados
  └─► Recebe mensagens MQTT
  └─► Responde HTTP local

Estado 4: WiFi caiu
  WiFi: ✗  MQTT: ✗
  └─► Aguarda reconexão manual do WiFi
  └─► Não tenta reconectar MQTT

VERIFICAR ESTADO:
  • isWiFiConnected() → bool
  • isMQTTConnected() → bool
```

## 🚦 Indicadores Visuais

```
LED no pino 2:
  ├─ PISCA 200ms → Mensagem MQTT recebida
  ├─ LIGADO → Comando /H recebido via HTTP
  └─ DESLIGADO → Comando /L recebido via HTTP
```

---

**Legenda dos Símbolos:**
- ✓ = Conectado/Sucesso
- ✗ = Desconectado/Falha
- ► = Fluxo de execução
- → = Retorna/Indica
