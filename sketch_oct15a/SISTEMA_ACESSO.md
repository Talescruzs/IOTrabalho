# 🚪 Sistema de Controle de Acesso - 4 ESPs

## 📋 Visão Geral

Sistema distribuído de controle de acesso com 4 ESP32s integradas via MQTT e HTTP, permitindo autenticação, monitoramento de porta e feedback visual.

## 🔧 Hardware Necessário

### ESP1 - Teclado + Vibração
- ESP32
- Teclado Matricial 4x4
- Motor de Vibração
- Pino motor: GPIO 25

### ESP2 - Porta
- ESP32  
- Módulo Relé
- Encoder Óptico (sensor de porta)
- Pino relé: GPIO 26
- Pino encoder: GPIO 27

### ESP3 - Ambiente
- ESP32
- Sensor DHT11 (temperatura e umidade)
- Pino DHT: GPIO 4

### ESP4 - LEDs
- ESP32
- 3 LEDs (Verde, Vermelho, Amarelo)
- 3 Resistores 220Ω
- Pino LED Verde: GPIO 32
- Pino LED Vermelho: GPIO 33
- Pino LED Amarelo: GPIO 25

## 🎯 Funcionamento

### 1️⃣ Acesso e Autenticação (ESP1)

**Usuário digita senha no teclado:**

#### Senha Correta (`*1234`)
```
ESP1 → Envia tentativa autorizada
Servidor → ESP1: comando "vibrate_short"
Servidor → ESP4: comando "led_green" (3s)
Servidor → ESP2: comando "unlock_door"
```

**Fluxo:**
1. ESP1 vibra 1 segundo
2. ESP4 acende LED verde por 3 segundos
3. ESP2 aciona relé (desbloqueio)

#### Senha Incorreta
```
ESP1 → Envia tentativa negada
Servidor → ESP1: comando "vibrate_long"
Servidor → ESP4: comando "led_red" (3s)
```

**Fluxo:**
1. ESP1 vibra 3 segundos
2. ESP4 acende LED vermelho por 3 segundos

### 2️⃣ Monitoramento de Abertura (ESP2)

**Porta aberta detectada pelo encoder:**

```
ESP2 → Envia door_open=1
```

**Porta aberta > 5 segundos:**
```
ESP2 → Envia alerta "door_open_timeout"
Servidor → ESP4: comando "led_alert"
```

**Fluxo:**
1. ESP4 acende LEDs verde + vermelho simultaneamente

**Porta fechada:**
```
ESP2 → Envia door_open=0  
Servidor → ESP4: comando "led_off"
```

**Fluxo:**
1. ESP4 apaga todos os LEDs

### 3️⃣ Monitoramento Ambiental (ESP3)

**Leituras periódicas (1 segundo):**

```
ESP3 → Envia temperature, humidity
```

**Temperatura > limite (30°C):**
```
ESP3 → Envia temp_alert=1
Servidor → ESP4: comando "led_yellow"
```

**Fluxo:**
1. ESP4 acende LED amarelo

## 📡 API de Comandos

### Comandos via HTTP POST

Envie para: `http://<IP_DA_ESP>/command`

**Formato:**
```json
{
  "command": "nome_do_comando",
  "params": {
    "parametro": "valor"
  }
}
```

### Comandos via MQTT

Publique em: `iot/response/<device_id>`

**Formato:**
```json
{
  "command": "nome_do_comando",
  "params": {
    "parametro": "valor"
  }
}
```

## 📜 Lista de Comandos

### ESP1 (Teclado)
| Comando | Parâmetros | Descrição |
|---------|-----------|-----------|
| `vibrate_short` | - | Vibra 1 segundo |
| `vibrate_long` | - | Vibra 3 segundos |

### ESP2 (Porta)
| Comando | Parâmetros | Descrição |
|---------|-----------|-----------|
| `unlock_door` | - | Desbloqueia porta |
| `lock_door` | - | Bloqueia porta |

### ESP4 (LEDs)
| Comando | Parâmetros | Descrição |
|---------|-----------|-----------|
| `led_green` | `duration` (ms) | Acende LED verde |
| `led_red` | `duration` (ms) | Acende LED vermelho |
| `led_yellow` | `duration` (ms) | Acende LED amarelo |
| `led_alert` | - | Verde + Vermelho |
| `led_off` | - | Apaga todos |

**Exemplo com duração:**
```json
{
  "command": "led_green",
  "params": {
    "duration": 5000
  }
}
```

## 🔌 Endpoints HTTP das ESPs

Cada ESP expõe os seguintes endpoints:

### `GET /`
Página HTML de controle

### `GET /status`
Retorna status em JSON

### `POST /command`
Recebe comandos do servidor

**Exemplo:**
```bash
curl -X POST http://192.168.1.101/command \
  -H "Content-Type: application/json" \
  -d '{"command":"vibrate_short"}'
```

## 📊 Dados Enviados pelas ESPs

### ESP1 - access_attempt
```json
{
  "device_id": "ESP32_KEYPAD",
  "sensor": "access_attempt",
  "data": {
    "password": "1234",
    "authorized": 1,
    "length": 4
  }
}
```

### ESP2 - door_sensor
```json
{
  "device_id": "ESP32_DOOR",
  "sensor": "door_sensor",
  "data": {
    "door_open": 0,
    "unlocked": 1
  }
}
```

### ESP2 - alert
```json
{
  "device_id": "ESP32_DOOR",
  "sensor": "alert",
  "data": {
    "alert": "door_open_timeout",
    "duration": 7
  }
}
```

### ESP3 - climate
```json
{
  "device_id": "ESP32_CLIMATE",
  "sensor": "climate",
  "data": {
    "temperature": 28.5,
    "humidity": 62.3,
    "temp_alert": 0
  }
}
```

### ESP4 - led_status
```json
{
  "device_id": "ESP32_LEDS",
  "sensor": "led_status",
  "data": {
    "green": 0,
    "red": 0,
    "yellow": 0
  }
}
```

## 🚀 Como Usar

### 1. Configure cada ESP

Edite `exemplo_sistema_acesso.ino.txt` e defina:

```cpp
#define ESP_TYPE 1  // 1=Teclado, 2=Porta, 3=Ambiente, 4=LEDs
```

### 2. Upload para cada ESP32

- ESP1: `ESP_TYPE = 1`
- ESP2: `ESP_TYPE = 2`
- ESP3: `ESP_TYPE = 3`
- ESP4: `ESP_TYPE = 4`

### 3. Servidor Python (Lógica de Controle)

Crie um script Python que:
1. Escuta dados MQTT das ESPs
2. Processa lógica de controle
3. Envia comandos via HTTP ou MQTT

**Exemplo simplificado:**

```python
def on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    
    if data.get('sensor') == 'access_attempt':
        if data['data']['authorized'] == 1:
            # Acesso autorizado
            send_command('ESP32_KEYPAD', 'vibrate_short')
            send_command('ESP32_LEDS', 'led_green', {'duration': 3000})
            send_command('ESP32_DOOR', 'unlock_door')
        else:
            # Acesso negado
            send_command('ESP32_KEYPAD', 'vibrate_long')
            send_command('ESP32_LEDS', 'led_red', {'duration': 3000})
    
    elif data.get('sensor') == 'alert':
        if data['data']['alert'] == 'door_open_timeout':
            send_command('ESP32_LEDS', 'led_alert')

def send_command(device_id, command, params=None):
    # Via MQTT
    topic = f"iot/response/{device_id}"
    payload = {
        "command": command,
        "params": params or {}
    }
    client.publish(topic, json.dumps(payload))
    
    # Ou via HTTP
    # ip = get_device_ip(device_id)
    # requests.post(f"http://{ip}/command", json=payload)
```

## 🔐 Segurança

### Senha Padrão
- Senha correta: `*1234`
- Altere em: `const String SENHA_CORRETA = "1234";`

### Recomendações
1. Use HTTPS para comunicação com servidor
2. Implemente autenticação nos endpoints HTTP
3. Criptografe senhas enviadas
4. Limite tentativas de acesso

## 🐛 Troubleshooting

### ESP não se conecta ao WiFi
- Verifique SSID e senha em `comunicacao.cpp`
- Verifique sinal WiFi

### Comandos não funcionam
- Verifique se callback está registrado: `comunicacaoSetCallback(processarComando)`
- Verifique logs Serial do servidor
- Teste manualmente com `curl`

### LEDs não acendem
- Verifique pinos GPIO
- Teste com comando direto via HTTP

## 📚 Referências

- `comunicacao.h/cpp` - Biblioteca de comunicação
- `teclado.h/cpp` - Biblioteca do teclado
- `exemplo_sistema_acesso.ino.txt` - Código completo das 4 ESPs

---

**Criado para:** Projeto IoT - Controle de Acesso Distribuído  
**Versão:** 1.0  
**Data:** 18/11/2025
