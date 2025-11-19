# Resumo da Refatoração - Classe Connection

## 🎯 O que foi feito

O arquivo `comunicacao.ino` foi completamente refatorado para usar **programação orientada a objetos**, criando a classe `Connection` que encapsula toda a lógica de comunicação.

## 📦 Nova Estrutura

```
sketch_oct15a/
├── comunicacao.ino              ← Classe Connection + funções auxiliares
├── exemplo_uso_connection.ino   ← Exemplos práticos de uso
└── README_Connection.md         ← Documentação completa
```

## 🔧 Classe Connection

### Antes (Código Procedural)
```cpp
// Variáveis globais espalhadas
WiFiClient espClient;
PubSubClient mqttClient(espClient);
WiFiServer server(80);
int LED = 2;

void comunicacaoInit() {
  // Muito código misturado
  Serial.begin(9600);
  WiFi.begin(ssid, password);
  mqttClient.setServer(...);
  // ... mais código
}

void comunicacaoTick() {
  // Lógica espalhada
  if (mqttClient.connected()) {
    mqttClient.loop();
  }
  // ... reconexão
  // ... envio periódico
  comunicacaoProcess();
}
```

### Depois (Orientado a Objetos)
```cpp
// Tudo encapsulado em uma classe
class Connection {
private:
  WiFiClient _espClient;
  PubSubClient _mqttClient;
  WiFiServer _httpServer;
  const char* _deviceId;
  bool _mqttConnected;
  // ... outros membros privados
  
public:
  Connection(const char* ssid, const char* password, ...);
  bool begin();
  bool sendSensorData(const String& sensor, const JSONVar& data);
  void tick();
  // ... outros métodos públicos
};

// Uso simples
Connection connection(ssid, password, deviceId, mqttBroker);
```

## ✨ Principais Melhorias

### 1. **Encapsulamento**
```cpp
// ❌ ANTES: Acesso direto a variáveis globais
mqttClient.publish("topic", message);

// ✅ DEPOIS: Através de métodos da classe
connection.sendSensorData("motor", dados);
```

### 2. **Interface Simplificada**
```cpp
// ❌ ANTES: Construir JSON manualmente
String sensorMsg = "{\"device_id\":\"esp32\",\"sensor\":\"motor\",\"data\":{\"rpm\":" + 
                  String(rpm) + ",\"temp\":" + String(temp) + "}}";
mqttClient.publish("iot/sensor/esp32", sensorMsg.c_str());

// ✅ DEPOIS: Método que aceita JSONVar ou arrays
JSONVar dados;
dados["rpm"] = rpm;
dados["temp"] = temp;
connection.sendSensorData("motor", dados);
```

### 3. **Gerenciamento de Estado**
```cpp
// ✅ NOVO: Verificar conexões facilmente
if (connection.isWiFiConnected()) {
  Serial.println("WiFi OK!");
}

if (connection.isMQTTConnected()) {
  Serial.println("MQTT OK!");
}

Serial.println("IP: " + connection.getDeviceIP());
```

### 4. **Reconexão Automática**
```cpp
// ❌ ANTES: Código de reconexão espalhado no tick()
static unsigned long lastReconnect = 0;
if (millis() - lastReconnect > 5000) {
  // ... lógica de reconexão
}

// ✅ DEPOIS: Gerenciado internamente pela classe
connection.tick();  // Reconecta automaticamente se necessário
```

### 5. **Múltiplos Métodos de Envio**
```cpp
// Método 1: JSONVar (mais flexível)
JSONVar dados;
dados["rpm"] = 1500;
dados["temp"] = 25.3;
connection.sendSensorData("motor", dados);

// Método 2: Arrays (mais eficiente)
const char* campos[] = {"rpm", "temp"};
double valores[] = {1500, 25.3};
connection.sendSensorData("motor", campos, valores, 2);

// Método 3: HTTP POST externo
connection.sendHTTPPost("192.168.1.100", 5000, "/api/data", jsonPayload);
```

## 📊 Comparação de Código

### Enviar Dados de Sensor

#### Antes (38 linhas):
```cpp
void enviarDadosMotor(double rpm, double temp) {
  if (mqttClient.connected()) {
    String sensorMsg = "{\"device_id\":\"esp32\",\"sensor\":\"motor\",\"data\":{\"rpm\":" + 
                      String(rpm) + ",\"temp\":" + String(temp) + "}}";
    
    mqttClient.publish("iot/sensor/esp32", sensorMsg.c_str());
    Serial.println("Dados de sensor enviados: " + sensorMsg);
  } else {
    Serial.println("MQTT não conectado!");
  }
}
```

#### Depois (3 linhas):
```cpp
void enviarDadosMotor(double rpm, double temp) {
  JSONVar dados;
  dados["rpm"] = rpm;
  dados["temp"] = temp;
  connection.sendSensorData("motor", dados);
}
```

## 🚀 Como Migrar Código Antigo

### 1. Substituir Variáveis Globais
```cpp
// ❌ ANTES
extern WiFiClient espClient;
extern PubSubClient mqttClient;

// ✅ DEPOIS
extern Connection connection;
```

### 2. Substituir Chamadas de Função
```cpp
// ❌ ANTES
mqttClient.publish(topic, payload);

// ✅ DEPOIS
connection.sendSensorData(sensor, dados);
```

### 3. Usar Funções de Compatibilidade
```cpp
// Se quiser manter código antigo funcionando
void setup() {
  comunicacaoInit();  // Chama connection.begin()
}

void loop() {
  comunicacaoTick();  // Chama connection.tick()
}
```

## 📝 Exemplos de Uso Prático

### Setup Básico
```cpp
void setup() {
  comunicacaoInit();
  
  while (!connection.isWiFiConnected()) {
    delay(1000);
  }
  
  Serial.println("IP: " + connection.getDeviceIP());
}
```

### Enviar Dados Periodicamente
```cpp
void loop() {
  comunicacaoTick();
  
  static unsigned long last = 0;
  if (millis() - last > 5000) {
    JSONVar dados;
    dados["rpm"] = analogRead(A0);
    enviarDadosSensor("motor", dados);
    last = millis();
  }
}
```

### Integração com Sensores Reais
```cpp
// DHT11
#include <DHT.h>
DHT dht(4, DHT11);

void enviarTemperatura() {
  float temp = dht.readTemperature();
  float hum = dht.readHumidity();
  
  JSONVar dados;
  dados["temperatura"] = temp;
  dados["umidade"] = hum;
  
  connection.sendSensorData("DHT11", dados);
}

// Encoder
volatile int encoderPos = 0;

void enviarPosicaoEncoder() {
  JSONVar dados;
  dados["posicao"] = encoderPos;
  
  connection.sendSensorData("Encoder", dados);
}
```

## 🎁 Benefícios

✅ **Código mais limpo e organizado**  
✅ **Fácil manutenção e debug**  
✅ **Reutilizável em outros projetos**  
✅ **Menos código duplicado**  
✅ **Melhor tratamento de erros**  
✅ **Reconexão automática**  
✅ **Interface consistente**  
✅ **Compatibilidade com código antigo**  

## 📚 Arquivos de Referência

- **`comunicacao.ino`** - Implementação da classe Connection
- **`README_Connection.md`** - Documentação completa da API
- **`exemplo_uso_connection.ino`** - Exemplos práticos de uso

## 🔗 Próximos Passos

1. Testar a classe com seu hardware
2. Adaptar seus sensores para usar os novos métodos
3. Explorar os exemplos em `exemplo_uso_connection.ino`
4. Ler a documentação completa em `README_Connection.md`

---

**Criado em:** 17 de novembro de 2025  
**Versão:** 1.0  
**Autor:** Refatoração do sistema de comunicação ESP32
