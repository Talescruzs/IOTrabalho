# Projeto sketch_oct15a - Sistema de Comunicação ESP32

## 📁 Estrutura de Arquivos

### ✅ Arquivos Ativos (compilados pelo Arduino)

- **`sketch_oct15a.ino`** - Arquivo principal com `setup()` e `loop()`
- **`comunicacao.ino`** - Classe `Connection` (WiFi, MQTT, HTTP)
- **`joystick.ino`** - Módulo joystick
- **`rpm.ino`** - Módulo RPM
- **`teclado.ino`** - Módulo teclado
- **`S_umidade_temperatura.ino`** - Sensor DHT11
- **`rele.ino`** - Controle de relé

### 📚 Arquivos de Documentação

- **`INDEX.md`** - Índice completo da documentação
- **`README_Connection.md`** - API da classe Connection
- **`ARQUITETURA.md`** - Diagramas e fluxos
- **`REFATORACAO.md`** - Antes/depois da refatoração
- **`GUIA_RAPIDO.md`** - Quick start

### 📖 Arquivos de Referência (não compilados)

- **`exemplo_uso_connection.cpp`** - Exemplos de código (copie daqui)
- **`motor_vibracao.ino.bak`** - Backup do módulo motor

## 🚀 Como Usar Este Projeto

### 1. Abrir no Arduino IDE

```bash
# Abra o arquivo principal:
sketch_oct15a.ino
```

O Arduino IDE automaticamente carregará todos os arquivos `.ino` da pasta.

### 2. Configurar WiFi e MQTT

Edite `comunicacao.ino`:

```cpp
char* ssid = "SEU_WIFI";           // ← Alterar
char* password = "SUA_SENHA";       // ← Alterar
const char* MQTT_BROKER = "192.168.1.XXX";  // ← Alterar
```

### 3. Compilar e Enviar

1. Selecione a placa: **ESP32 Dev Module**
2. Selecione a porta COM
3. Clique em **Upload**

### 4. Monitorar

Abra o Serial Monitor (9600 baud) para ver:
- Status de conexão WiFi
- IP do dispositivo
- Confirmações MQTT
- Dados enviados

## 💡 Exemplos de Uso

### Exemplo Básico (já em sketch_oct15a.ino)

```cpp
void setup() {
  comunicacaoInit();  // Conecta WiFi e MQTT
}

void loop() {
  comunicacaoTick();  // Mantém conexões ativas
  
  // Enviar dados periodicamente
  static unsigned long lastSend = 0;
  if (millis() - lastSend > 10000) {
    JSONVar dados;
    dados["rpm"] = random(1000, 4000);
    dados["temp"] = random(20, 45);
    enviarDadosSensor("motor", dados);
    lastSend = millis();
  }
}
```

### Adicionar Mais Sensores

Copie exemplos de `exemplo_uso_connection.cpp` para `sketch_oct15a.ino`:

```cpp
// Exemplo: DHT11
void enviarTemperatura() {
  JSONVar dados;
  dados["temperatura"] = 23.5;
  dados["umidade"] = 65.2;
  enviarDadosSensor("DHT11", dados);
}

// Exemplo: Teclado
void enviarTentativaAcesso(bool autorizado) {
  JSONVar dados;
  dados["authorized"] = autorizado ? 1 : 0;
  dados["vibration_duration"] = autorizado ? 200 : 600;
  enviarDadosSensor("Teclado 4x4", dados);
}
```

## 📡 Comunicação

### MQTT

**Tópicos Publicados:**
- `iot/register` - Registro do dispositivo
- `iot/sensor/esp32` - Dados dos sensores

**Tópicos Subscritos:**
- `iot/confirm/esp32` - Confirmações
- `iot/response/esp32` - Respostas do servidor

### HTTP Local

Servidor na porta 80 responde em:
- `http://<IP_ESP>/` - Página HTML
- `http://<IP_ESP>/H` - Liga LED
- `http://<IP_ESP>/L` - Desliga LED
- `http://<IP_ESP>/status` - JSON com dados

## 🔧 Métodos Disponíveis

### Enviar Dados (via MQTT)

```cpp
// Método 1: JSONVar
JSONVar dados;
dados["campo1"] = valor1;
enviarDadosSensor("NomeSensor", dados);

// Método 2: Arrays
const char* campos[] = {"campo1", "campo2"};
double valores[] = {valor1, valor2};
enviarDadosSensor("NomeSensor", campos, valores, 2);
```

### Verificar Status

```cpp
connection.isWiFiConnected()   // true/false
connection.isMQTTConnected()   // true/false
connection.getDeviceIP()       // "192.168.1.XXX"
connection.getDeviceId()       // "esp32"
```

### Enviar HTTP POST Externo

```cpp
JSONVar payload;
payload["data"] = 123;
enviarHTTPPost("192.168.1.100", 5000, "/api/endpoint", payload);
```

## 📚 Documentação Completa

Leia os arquivos na seguinte ordem:

1. **`INDEX.md`** - Visão geral e navegação
2. **`GUIA_RAPIDO.md`** - Quick start
3. **`README_Connection.md`** - Referência completa da API
4. **`ARQUITETURA.md`** - Entenda os fluxos internos
5. **`exemplo_uso_connection.cpp`** - Copie exemplos daqui

## 🐛 Troubleshooting

### WiFi não conecta
- Verifique SSID e senha em `comunicacao.ino`
- Verifique se está no alcance do roteador

### MQTT não conecta
- Verifique IP do broker
- Teste com: `mosquitto_sub -h <BROKER_IP> -t '#' -v`

### Erro de compilação "JSONVar not declared"
- Instale biblioteca: **Arduino_JSON** (Tools → Manage Libraries)

### Erro de compilação "PubSubClient not found"
- Instale biblioteca: **PubSubClient** (Tools → Manage Libraries)

### Múltiplas definições de setup()/loop()
- Arduino compila todos `.ino` juntos
- Mantenha apenas um `setup()` e um `loop()`
- Arquivos de exemplo devem ter extensão `.cpp` ou `.txt`

## 📦 Bibliotecas Necessárias

Instale via Arduino IDE (Tools → Manage Libraries):

1. **WiFi** - Built-in para ESP32
2. **PubSubClient** - Cliente MQTT
3. **Arduino_JSON** - Parser JSON

## ⚙️ Configuração da Placa

**Board:** ESP32 Dev Module  
**Upload Speed:** 115200  
**CPU Frequency:** 240MHz  
**Flash Frequency:** 80MHz  
**Flash Mode:** QIO  
**Flash Size:** 4MB  
**Partition Scheme:** Default  

## 🎯 Projeto Integrado

Este projeto faz parte de um sistema IoT completo:

- **ESP32** (este projeto) - Coleta e envia dados
- **Servidor Python/Flask** - Recebe via MQTT e HTTP
- **Banco MySQL** - Armazena leituras
- **Dashboard Web** - Visualiza em tempo real

Veja pasta `../API/` e `../Front/` para os outros componentes.

---

**Versão:** 1.0  
**Data:** 17/11/2025  
**Plataforma:** ESP32  
**IDE:** Arduino IDE 2.x
