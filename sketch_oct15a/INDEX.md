# 📚 Índice Completo - Classe Connection

## ✅ Arquivos Criados/Modificados

### 📄 Código Principal
- **`comunicacao.ino`** (13K)
  - Implementação completa da classe `Connection`
  - Gerenciamento de WiFi, MQTT e HTTP
  - Métodos para envio de dados
  - Reconexão automática

- **`sketch_oct15a.ino`** (1.1K)
  - Arquivo principal do projeto
  - Contém `setup()` e `loop()`
  - Exemplo de uso básico da Connection

### 📘 Documentação

1. **`README_Connection.md`** (7.3K)
   - Documentação completa da API
   - Todos os métodos explicados
   - Parâmetros e retornos
   - Exemplos de uso

2. **`ARQUITETURA.md`** (14K)
   - Diagrama de classes
   - Fluxos de comunicação
   - Estrutura de dados MQTT
   - Ciclo de vida da conexão
   - Estados possíveis

3. **`REFATORACAO.md`** (6.5K)
   - Comparação antes/depois
   - Benefícios da refatoração
   - Guia de migração
   - Exemplos de código

4. **`GUIA_RAPIDO.md`** (6.5K)
   - Quick start em 3 passos
   - Receitas de código
   - Tabela de substituição
   - Troubleshooting
   - Dicas práticas

### 💻 Exemplos de Código

5. **`exemplo_uso_connection.cpp`** (6.0K)
   - ⚠️ Arquivo de referência (não compilar)
   - 5 exemplos práticos completos
   - Integração com sensores reais
   - Funções auxiliares
   - Casos de uso do laboratório
   - **NOTA:** Copie os exemplos para `sketch_oct15a.ino`

---

## 🎯 O que a Classe Connection Faz

### Funcionalidades Principais

✅ **Gerenciamento de WiFi**
   - Conexão automática
   - Verificação de status
   - Obtenção de IP

✅ **Comunicação MQTT**
   - Conexão ao broker
   - Registro automático do dispositivo
   - Publicação de dados de sensores
   - Subscrição em tópicos de resposta
   - Reconexão automática (a cada 5s)

✅ **Servidor HTTP Local**
   - Responde em porta 80
   - Endpoints: /, /H, /L, /status
   - Retorna JSON com dados
   - Controle de LED

✅ **Cliente HTTP**
   - Envia POST para servidores externos
   - Suporte a JSON
   - Timeout configurável

✅ **Feedback Visual**
   - LED pisca ao receber MQTT
   - LED liga/desliga via HTTP

---

## 📖 Como Navegar na Documentação

### 1️⃣ Começando do Zero?
👉 Leia **`GUIA_RAPIDO.md`** primeiro
   - Quick start em 3 passos
   - Receitas prontas para copiar/colar

### 2️⃣ Quer Entender a Estrutura?
👉 Leia **`ARQUITETURA.md`**
   - Diagramas visuais
   - Fluxos de comunicação
   - Estruturas de dados

### 3️⃣ Migrando Código Antigo?
👉 Leia **`REFATORACAO.md`**
   - Comparação antes/depois
   - Como substituir código antigo
   - Benefícios da mudança

### 4️⃣ Referência Completa da API?
👉 Leia **`README_Connection.md`**
   - Todos os métodos
   - Parâmetros detalhados
   - Exemplos de cada função

### 5️⃣ Quer Ver Código Funcionando?
👉 Abra **`exemplo_uso_connection.cpp`**
   - 5 exemplos práticos (arquivo de referência)
   - Copie exemplos para `sketch_oct15a.ino`
   - Código completo
   - Pronto para adaptar

👉 Ou veja **`sketch_oct15a.ino`**
   - Exemplo básico já funcionando
   - Pronto para compilar

---

## 🚀 Quick Start

### Passo 1: Incluir o arquivo
```cpp
// Já está incluído no projeto Arduino
// comunicacao.ino
```

### Passo 2: No setup()
```cpp
void setup() {
  comunicacaoInit();
}
```

### Passo 3: No loop()
```cpp
void loop() {
  comunicacaoTick();
  
  // Enviar dados
  JSONVar dados;
  dados["rpm"] = 1500;
  connection.sendSensorData("motor", dados);
  
  delay(5000);
}
```

---

## 📊 Métodos Mais Usados

| Método | Quando Usar |
|--------|-------------|
| `connection.begin()` | No setup() - inicializa tudo |
| `connection.tick()` | No loop() - mantém ativo |
| `sendSensorData(sensor, JSONVar)` | Enviar múltiplos campos |
| `sendSensorData(sensor, keys[], vals[], count)` | Enviar poucos campos |
| `sendHTTPPost(host, port, endpoint, json)` | POST externo |
| `isWiFiConnected()` | Verificar WiFi |
| `isMQTTConnected()` | Verificar MQTT |
| `getDeviceIP()` | Obter IP |

---

## 💡 Casos de Uso

### Laboratório IoT (4 ESPs)

**ESP1 - Teclado + Vibração**
```cpp
JSONVar dados;
dados["authorized"] = 1;
dados["vibration_duration"] = 200;
connection.sendSensorData("Teclado 4x4", dados);
```

**ESP2 - Porta + Relé**
```cpp
JSONVar dados;
dados["relay"] = 0;
dados["door_angle"] = 75;
connection.sendSensorData("Relé JQC3F", dados);
```

**ESP3 - Clima**
```cpp
JSONVar dados;
dados["temperatura"] = 23.5;
dados["umidade"] = 65.2;
connection.sendSensorData("DHT11", dados);
```

**ESP4 - LEDs Status**
```cpp
JSONVar dados;
dados["led_green"] = 255;
dados["led_yellow"] = 0;
dados["led_red"] = 0;
connection.sendSensorData("KY023", dados);
```

---

## 🔗 Integração com Sistema Python

### Servidor API (porta 5000)
- Recebe dados via MQTT
- Salva no banco MySQL
- Disponibiliza em `/api/chart-data`

### Dashboard Web (porta 5001)
- Mostra gráficos em tempo real
- Timeline de evolução
- Tabela de leituras

### Simuladores Python
- `simulate_esp32.py` - Motor
- `simulate_lab.py` - Laboratório completo

---

## 📦 Estrutura do Projeto

```
sketch_oct15a/
├── sketch_oct15a.ino            ← ARQUIVO PRINCIPAL (setup + loop)
├── comunicacao.ino              ← CLASSE CONNECTION
├── exemplo_uso_connection.cpp   ← EXEMPLOS (referência, copie daqui)
├── README_Connection.md         ← DOCUMENTAÇÃO API
├── ARQUITETURA.md              ← DIAGRAMAS
├── REFATORACAO.md              ← ANTES/DEPOIS
├── GUIA_RAPIDO.md              ← QUICK START
├── INDEX.md                    ← ESTE ARQUIVO
└── [outros arquivos do projeto]

⚠️ IMPORTANTE: 
- Arduino compila todos os arquivos .ino juntos
- exemplo_uso_connection.cpp é apenas referência
- Copie exemplos para sketch_oct15a.ino conforme necessário
```

---

## 🎓 Níveis de Conhecimento

### 👶 Iniciante
1. Leia `GUIA_RAPIDO.md`
2. Copie exemplos de `exemplo_uso_connection.ino`
3. Teste com seu hardware

### 🧑‍💻 Intermediário
1. Leia `README_Connection.md`
2. Entenda cada método
3. Customize para seus sensores

### 🚀 Avançado
1. Leia `ARQUITETURA.md`
2. Entenda fluxos internos
3. Modifique a classe para novas funcionalidades

---

## 🐛 Problemas Comuns

| Problema | Solução |
|----------|---------|
| WiFi não conecta | Verificar SSID e senha em `comunicacao.ino` |
| MQTT não conecta | Verificar IP do broker MQTT |
| Dados não chegam | Verificar `isMQTTConnected()` retorna true |
| LED não pisca | MQTT não recebendo confirmação do servidor |
| Compile error | Instalar bibliotecas: WiFi, PubSubClient, Arduino_JSON |

---

## 📚 Bibliotecas Necessárias

```cpp
#include <WiFi.h>              // ESP32 WiFi (built-in)
#include <PubSubClient.h>      // MQTT client
#include <Arduino_JSON.h>      // JSON parsing
```

### Instalar via Arduino IDE:
1. Tools → Manage Libraries
2. Procurar "PubSubClient" → Install
3. Procurar "Arduino_JSON" → Install

---

## ✨ Próximos Passos

1. [ ] Testar com hardware real
2. [ ] Adaptar para seus sensores
3. [ ] Integrar com sistema Python
4. [ ] Visualizar dados no dashboard
5. [ ] Adicionar novos sensores

---

## 📞 Suporte

- **Documentação:** Leia os arquivos `.md` nesta pasta
- **Exemplos:** Veja `exemplo_uso_connection.ino`
- **Debug:** Ative Serial Monitor (9600 baud)

---

## 📝 Changelog

### Versão 1.0 (17/11/2025)
- ✅ Classe Connection criada
- ✅ Refatoração completa de comunicacao.ino
- ✅ 4 arquivos de documentação
- ✅ Arquivo de exemplos
- ✅ Compatibilidade com código antigo mantida

---

**Criado em:** 17 de novembro de 2025  
**Total de linhas de código:** ~500 linhas na classe  
**Total de documentação:** ~1500 linhas  
**Arquivos criados:** 5 novos arquivos
