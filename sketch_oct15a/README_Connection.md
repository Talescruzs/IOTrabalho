# Classe Connection - Documentação

## Visão Geral

A classe `Connection` encapsula toda a comunicação da ESP32 com servidores via WiFi, MQTT e HTTP. Ela fornece uma interface orientada a objetos para gerenciar conexões e enviar dados de sensores.

## Características

✅ **WiFi**: Conexão automática com reconexão  
✅ **MQTT**: Publicação/subscrição com registro automático do dispositivo  
✅ **HTTP Server**: Servidor local para consultas de status  
✅ **HTTP Client**: Cliente para enviar dados via POST para servidores externos  
✅ **Auto-reconexão**: Reconecta automaticamente MQTT se a conexão cair  
✅ **Callbacks**: Recebe mensagens MQTT com feedback visual (LED)

## Estrutura Básica

```cpp
// Instância global (já criada no arquivo)
Connection connection(ssid, password, DEVICE_ID, MQTT_BROKER);

void setup() {
  // Inicializa todas as conexões
  connection.begin();
}

void loop() {
  // Mantém conexões ativas e processa requisições
  connection.tick();
}
```

## Construtor

```cpp
Connection(const char* ssid, 
           const char* password, 
           const char* deviceId, 
           const char* mqttBroker, 
           uint16_t mqttPort = 1883, 
           int ledPin = 2, 
           uint16_t httpPort = 80)
```

**Parâmetros:**
- `ssid`: Nome da rede WiFi
- `password`: Senha da rede WiFi
- `deviceId`: ID único do dispositivo (ex: "esp32")
- `mqttBroker`: Endereço IP do broker MQTT
- `mqttPort`: Porta MQTT (padrão: 1883)
- `ledPin`: Pino do LED de feedback (padrão: 2)
- `httpPort`: Porta do servidor HTTP local (padrão: 80)

## Métodos Principais

### 1. Inicialização

```cpp
bool begin()
```
Inicializa WiFi, servidor HTTP e MQTT. Retorna `true` se WiFi conectou com sucesso.

**Exemplo:**
```cpp
void setup() {
  if (connection.begin()) {
    Serial.println("Conexão estabelecida!");
  } else {
    Serial.println("Falha na conexão!");
  }
}
```

### 2. Enviar Dados de Sensor via MQTT (JSONVar)

```cpp
bool sendSensorData(const String& sensorName, const JSONVar& data)
```

**Exemplo:**
```cpp
JSONVar dados;
dados["rpm"] = 1500.5;
dados["temp"] = 25.3;
dados["voltage"] = 12.1;

connection.sendSensorData("motor", dados);
```

**Mensagem MQTT enviada:**
```json
{
  "device_id": "esp32",
  "sensor": "motor",
  "data": {
    "rpm": 1500.5,
    "temp": 25.3,
    "voltage": 12.1
  },
  "timestamp": "123456"
}
```

### 3. Enviar Dados de Sensor via MQTT (Arrays)

```cpp
bool sendSensorData(const String& sensorName, const char* keys[], const double values[], size_t count)
```

**Exemplo:**
```cpp
const char* campos[] = {"rpm", "temp", "voltage"};
double valores[] = {1500.5, 25.3, 12.1};

connection.sendSensorData("motor", campos, valores, 3);
```

### 4. Enviar HTTP POST para Servidor Externo

```cpp
bool sendHTTPPost(const char* serverHost, uint16_t serverPort, const String& endpoint, const String& jsonPayload)
```

**Exemplo:**
```cpp
JSONVar payload;
payload["device"] = "esp32";
payload["sensor"] = "motor";
payload["rpm"] = 1500;

String json = JSON.stringify(payload);
connection.sendHTTPPost("192.168.1.100", 5000, "/api/ingest", json);
```

### 5. Loop de Manutenção

```cpp
void tick()
```
Deve ser chamado no `loop()` principal. Mantém conexões ativas e processa requisições HTTP.

**Exemplo:**
```cpp
void loop() {
  connection.tick();
  
  // Seu código aqui
  delay(10);
}
```

### 6. Verificar Status das Conexões

```cpp
bool isWiFiConnected()  // Retorna true se WiFi está conectado
bool isMQTTConnected()  // Retorna true se MQTT está conectado
String getDeviceIP()    // Retorna IP do dispositivo
String getDeviceId()    // Retorna ID do dispositivo
```

**Exemplo:**
```cpp
if (connection.isMQTTConnected()) {
  Serial.println("MQTT OK! IP: " + connection.getDeviceIP());
}
```

## Funções Auxiliares (Compatibilidade)

Para manter compatibilidade com código antigo, as seguintes funções estão disponíveis:

```cpp
void comunicacaoInit()     // Chama connection.begin()
void comunicacaoTick()     // Chama connection.tick()
void comunicacaoProcess()  // Chama connection.processHTTP()

// Funções de envio simplificadas
bool enviarDadosSensor(const String& sensorName, const JSONVar& data)
bool enviarDadosSensor(const String& sensorName, const char* keys[], const double values[], size_t count)
bool enviarHTTPPost(const char* serverHost, uint16_t serverPort, const String& endpoint, const JSONVar& data)
```

## Exemplo Completo de Uso

### sketch_oct15a.ino
```cpp
#include "comunicacao.ino"

void setup() {
  // Inicializa comunicação
  comunicacaoInit();
  
  // OU usando o objeto diretamente
  // connection.begin();
}

void loop() {
  // Mantém conexão ativa
  comunicacaoTick();
  
  // Envia dados de RPM a cada 5 segundos
  static unsigned long lastSend = 0;
  if (millis() - lastSend > 5000) {
    // Método 1: Usando JSONVar
    JSONVar dados;
    dados["rpm"] = analogRead(A0);
    dados["temp"] = 25.0;
    enviarDadosSensor("motor", dados);
    
    // Método 2: Usando arrays
    const char* keys[] = {"rpm", "temp"};
    double vals[] = {analogRead(A0), 25.0};
    enviarDadosSensor("motor", keys, vals, 2);
    
    lastSend = millis();
  }
  
  delay(10);
}
```

### Integrando com Outros Sensores

```cpp
// Exemplo: Encoder
void enviarDadosEncoder(double posicao, double velocidade) {
  JSONVar dados;
  dados["posicao"] = posicao;
  dados["velocidade"] = velocidade;
  
  connection.sendSensorData("Encoder", dados);
}

// Exemplo: DHT11
void enviarDadosTemperatura(float temp, float umidade) {
  const char* campos[] = {"temperatura", "umidade"};
  double valores[] = {temp, umidade};
  
  connection.sendSensorData("DHT11", campos, valores, 2);
}

// Exemplo: Teclado
void enviarTentativaAcesso(bool autorizado, int tentativas) {
  JSONVar dados;
  dados["authorized"] = autorizado ? 1 : 0;
  dados["attempts"] = tentativas;
  dados["password_length"] = 4;
  
  connection.sendSensorData("Teclado 4x4", dados);
}
```

## Servidor HTTP Local

O servidor HTTP local responde a:

- **GET /**: Página HTML com links de controle
- **GET /H**: Liga LED
- **GET /L**: Desliga LED  
- **GET /status**: Retorna JSON com status do sensor motor

**Exemplo de resposta /status:**
```json
{
  "device": "esp32",
  "sensor": "motor",
  "data": {
    "rpm": 1234.5,
    "temp": 25.3
  },
  "ts": 123456
}
```

## Mensagens MQTT

### Tópicos Subscritos Automaticamente:
- `iot/confirm/{deviceId}`: Confirmações do servidor
- `iot/response/{deviceId}`: Respostas do servidor

### Tópicos Publicados:
- `iot/register`: Registro inicial do dispositivo
- `iot/sensor/{deviceId}`: Dados dos sensores

## Reconexão Automática

A classe tenta reconectar automaticamente ao MQTT a cada 5 segundos se a conexão cair. O LED pisca quando recebe mensagens MQTT.

## Troubleshooting

**WiFi não conecta:**
- Verifique SSID e senha
- Verifique se o roteador está alcançável

**MQTT não conecta:**
- Verifique endereço IP do broker
- Verifique se a porta 1883 está aberta
- Teste com `mosquitto_sub -h BROKER_IP -t '#' -v`

**Dados não chegam no servidor:**
- Verifique se `connection.isMQTTConnected()` retorna true
- Monitore Serial para mensagens de erro
- Verifique tópicos MQTT no broker

## Performance

- Reconexão WiFi: ~10 segundos
- Reconexão MQTT: ~5 segundos
- Envio de mensagem MQTT: <100ms
- Processamento HTTP: <50ms por requisição
