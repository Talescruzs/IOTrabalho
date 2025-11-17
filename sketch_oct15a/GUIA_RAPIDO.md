# Guia Rápido de Migração

## 🚀 Como Usar a Nova Classe Connection

### ⚡ Quick Start (3 passos)

#### 1. Configurar (apenas uma vez)
```cpp
// Já está configurado em comunicacao.ino
Connection connection(ssid, password, "esp32", MQTT_BROKER);
```

#### 2. Inicializar no setup()
```cpp
void setup() {
  comunicacaoInit();  // ← Isso já faz tudo!
}
```

#### 3. Manter ativo no loop()
```cpp
void loop() {
  comunicacaoTick();  // ← Mantém conexões ativas
  
  // Seu código aqui
}
```

---

## 📝 Receitas de Código

### Enviar dados de RPM e Temperatura
```cpp
JSONVar dados;
dados["rpm"] = 1500;
dados["temp"] = 25.3;
connection.sendSensorData("motor", dados);
```

### Enviar dados de Temperatura e Umidade (DHT11)
```cpp
const char* campos[] = {"temperatura", "umidade"};
double valores[] = {23.5, 65.2};
connection.sendSensorData("DHT11", campos, valores, 2);
```

### Enviar tentativa de acesso (Teclado)
```cpp
JSONVar dados;
dados["authorized"] = 1;  // 0 ou 1
dados["password_length"] = 4;
dados["vibration_duration"] = 200;
connection.sendSensorData("Teclado 4x4", dados);
```

### Enviar estado da porta (Relé + Encoder)
```cpp
JSONVar dados;
dados["relay"] = 0;  // 0=destravado, 1=travado
dados["door_angle"] = 75;  // graus
dados["door_open"] = 1;  // 0 ou 1
connection.sendSensorData("Relé JQC3F", dados);
```

### Enviar LEDs de status
```cpp
JSONVar dados;
dados["led_green"] = 255;
dados["led_yellow"] = 0;
dados["led_red"] = 0;
connection.sendSensorData("KY023", dados);
```

### Verificar se está conectado
```cpp
if (connection.isMQTTConnected()) {
  Serial.println("MQTT OK!");
}

Serial.println("IP: " + connection.getDeviceIP());
```

---

## 🔧 Tabela de Substituição

| ❌ **Código Antigo** | ✅ **Código Novo** |
|---------------------|-------------------|
| `mqttClient.publish(topic, msg)` | `connection.sendSensorData(sensor, dados)` |
| `WiFi.status() == WL_CONNECTED` | `connection.isWiFiConnected()` |
| `mqttClient.connected()` | `connection.isMQTTConnected()` |
| `WiFi.localIP().toString()` | `connection.getDeviceIP()` |
| `mqttClient.loop()` | `connection.tick()` (já inclui) |

---

## 📋 Checklist de Migração

- [ ] Incluir `comunicacao.ino` no projeto
- [ ] Chamar `comunicacaoInit()` no `setup()`
- [ ] Chamar `comunicacaoTick()` no `loop()`
- [ ] Substituir chamadas diretas ao `mqttClient`
- [ ] Usar `connection.sendSensorData()` para enviar dados
- [ ] Testar reconexão desligando/ligando WiFi
- [ ] Testar envio de dados via MQTT
- [ ] Verificar LED piscando ao receber mensagens

---

## 🎓 Exemplos Completos

### Exemplo 1: Motor com RPM e Temperatura
```cpp
void setup() {
  comunicacaoInit();
}

void loop() {
  comunicacaoTick();
  
  // Envia a cada 5 segundos
  static unsigned long last = 0;
  if (millis() - last > 5000) {
    JSONVar dados;
    dados["rpm"] = analogRead(A0);
    dados["temp"] = 25.0;
    connection.sendSensorData("motor", dados);
    last = millis();
  }
}
```

### Exemplo 2: DHT11 com leitura real
```cpp
#include <DHT.h>
DHT dht(4, DHT11);

void setup() {
  comunicacaoInit();
  dht.begin();
}

void loop() {
  comunicacaoTick();
  
  static unsigned long last = 0;
  if (millis() - last > 10000) {
    float t = dht.readTemperature();
    float h = dht.readHumidity();
    
    if (!isnan(t) && !isnan(h)) {
      JSONVar dados;
      dados["temperatura"] = t;
      dados["umidade"] = h;
      connection.sendSensorData("DHT11", dados);
    }
    last = millis();
  }
}
```

### Exemplo 3: Sistema de Acesso Completo
```cpp
// ESP1: Teclado
void enviarTentativaAcesso(bool ok) {
  JSONVar dados;
  dados["authorized"] = ok ? 1 : 0;
  dados["vibration_duration"] = ok ? 200 : 600;
  connection.sendSensorData("Teclado 4x4", dados);
}

// ESP2: Porta
void atualizarEstadoPorta(bool travada, int angulo) {
  JSONVar dados;
  dados["relay"] = travada ? 1 : 0;
  dados["door_angle"] = angulo;
  connection.sendSensorData("Relé JQC3F", dados);
}

// ESP3: Clima
void enviarDadosAmbiente(float temp, float umidade) {
  JSONVar dados;
  dados["temperatura"] = temp;
  dados["umidade"] = umidade;
  connection.sendSensorData("DHT11", dados);
}

// ESP4: LEDs
void atualizarLEDs(int verde, int amarelo, int vermelho) {
  JSONVar dados;
  dados["led_green"] = verde;
  dados["led_yellow"] = amarelo;
  dados["led_red"] = vermelho;
  connection.sendSensorData("KY023", dados);
}
```

---

## 🐛 Troubleshooting

### Problema: WiFi não conecta
```cpp
void setup() {
  if (!connection.begin()) {
    Serial.println("WiFi falhou!");
    // Verificar SSID e senha
  }
}
```

### Problema: MQTT não conecta
```cpp
void loop() {
  if (!connection.isMQTTConnected()) {
    Serial.println("MQTT offline - tentando reconectar...");
  }
  comunicacaoTick();  // Reconecta automaticamente
}
```

### Problema: Dados não chegam no servidor
```cpp
// 1. Verificar conexão
Serial.println("WiFi: " + String(connection.isWiFiConnected()));
Serial.println("MQTT: " + String(connection.isMQTTConnected()));

// 2. Verificar tópico MQTT
// Deve ser: iot/sensor/{deviceId}
// No servidor: mosquitto_sub -t 'iot/sensor/#' -v

// 3. Verificar formato dos dados
JSONVar dados;
dados["campo1"] = valor1;
bool sucesso = connection.sendSensorData("sensor", dados);
Serial.println("Enviado: " + String(sucesso));
```

---

## 📖 Referências

- **`README_Connection.md`** - Documentação completa da API
- **`ARQUITETURA.md`** - Diagramas e fluxos
- **`exemplo_uso_connection.ino`** - 5 exemplos práticos
- **`REFATORACAO.md`** - Antes vs Depois

---

## 💡 Dicas

1. **Sempre chame `tick()` no loop** - Mantém conexões ativas
2. **Use `JSONVar` para múltiplos campos** - Mais flexível
3. **Use arrays para poucos campos** - Mais eficiente
4. **Verifique retorno de `sendSensorData()`** - Para debug
5. **Monitore Serial para mensagens** - Veja confirmações MQTT

---

## ✨ Recursos Avançados

### Enviar via HTTP POST (além de MQTT)
```cpp
JSONVar payload;
payload["device"] = "esp32";
payload["data"] = valorSensor;

connection.sendHTTPPost("192.168.1.100", 5000, "/api/custom", 
                        JSON.stringify(payload));
```

### Processar resposta HTTP local
O servidor HTTP local já responde automaticamente em:
- `GET /` - Página HTML
- `GET /H` - Liga LED
- `GET /L` - Desliga LED
- `GET /status` - Retorna JSON com dados

### Callback MQTT customizado
As mensagens MQTT já são processadas automaticamente e piscam o LED. Para customizar, modifique o método `onMqttMessage()` na classe.

---

**Última atualização:** 17/11/2025  
**Versão da classe:** 1.0
