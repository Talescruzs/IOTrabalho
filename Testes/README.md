# 📊 Testes do Sistema IoT

Este diretório contém scripts para testar o funcionamento do sistema IoT.

## 🔧 Scripts Disponíveis

### 1. `simulate_esp32.py` - Simulador de ESP32
Simula uma ESP32 enviando dados via MQTT e HTTP para o servidor.

**Funcionalidades:**
- ✅ Conecta ao broker MQTT
- ✅ Registra dispositivo com IP
- ✅ Envia dados de sensores simulados (RPM, temperatura, voltagem, corrente)
- ✅ Alterna entre envio MQTT e HTTP
- ✅ Recebe confirmações do servidor

**Como usar:**
```bash
# Execute o servidor API primeiro
cd /home/vboxuser/repos/IOTrabalho
.venv/bin/python API/Server.py

# Em outro terminal, execute o simulador
.venv/bin/python Testes/simulate_esp32.py
```

**Sensores simulados:**
- **RPM**: 0 a 4000 rpm
- **Temperatura**: 15°C a 45°C
- **Voltagem**: ~12V ± 0.5V
- **Corrente**: ~2.5A ± 0.3A

---

### 2. `test_database.py` - Verificador de Banco de Dados
Verifica se os dados estão sendo corretamente salvos no MySQL.

**O que verifica:**
- ✅ Conexão com o banco de dados
- ✅ ESPs registradas
- ✅ Sensores cadastrados
- ✅ Leituras mais recentes
- ✅ Detalhes dos valores de cada leitura

**Como usar:**
```bash
.venv/bin/python Testes/test_database.py
```

**Exemplo de saída:**
```
============================================================
VERIFICADOR DE DADOS DO BANCO IOT
============================================================

============================================================
TESTE DE CONEXÃO COM BANCO DE DADOS
============================================================
Host: localhost
Porta: 3306
Usuário: tales
Banco: banco_atu
============================================================

✓ Conexão estabelecida com sucesso!

============================================================
ESPs REGISTRADAS
============================================================
ID    Nome                      IP             
------------------------------------------------------------
1     unknown                   N/A            
2     esp32-simulator           192.168.1.100  

Total: 2 ESP(s) registrada(s)

============================================================
SENSORES CADASTRADOS
============================================================
ID    Nome                          
------------------------------------------------------------
1     motor                         

Total: 1 sensor(es) cadastrado(s)

============================================================
ÚLTIMAS 10 LEITURAS
============================================================
ID       Sensor               ESP                  Timestamp           
------------------------------------------------------------
5        motor                esp32-simulator      2025-11-16 15:35:12 
4        motor                esp32-simulator      2025-11-16 15:35:07 
3        motor                esp32-simulator      2025-11-16 15:35:02 

Total: 3 leitura(s)
```

---

## 🚀 Fluxo de Teste Completo

### Passo 1: Preparar o ambiente
```bash
cd /home/vboxuser/repos/IOTrabalho

# Ativa o ambiente virtual (se necessário)
source .venv/bin/activate

# Instala dependências
pip install -r API/requirements.txt
```

### Passo 2: Inicializar o banco
```bash
# Execute o script de inicialização do banco
.venv/bin/python Banco/init_db.py

# Ou execute diretamente no MySQL
mysql -u tales -p banco_atu < Banco/CreateDB.sql
mysql -u tales -p banco_atu < Banco/InsertSensores.sql
```

### Passo 3: Iniciar o servidor MQTT (Mosquitto)
```bash
# Se não estiver rodando
sudo systemctl start mosquitto

# Verificar status
sudo systemctl status mosquitto
```

### Passo 4: Iniciar o servidor API
```bash
.venv/bin/python API/Server.py
```

O servidor deve exibir:
```
✓ Variáveis carregadas de /home/vboxuser/repos/IOTrabalho/.env
[config] MQTT_BROKER=localhost, MQTT_PORT=1883, MQTT_TOPIC=iot/register
✓ Banco MySQL inicializado.
[mqtt] listener iniciado em thread daemon (broker=localhost:1883)
CORS habilitado para todos os origins.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
```

### Passo 5: Executar o simulador (em outro terminal)
```bash
cd /home/vboxuser/repos/IOTrabalho
.venv/bin/python Testes/simulate_esp32.py
```

### Passo 6: Verificar os dados (em outro terminal)
```bash
cd /home/vboxuser/repos/IOTrabalho
.venv/bin/python Testes/test_database.py
```

---

## 📝 Estrutura de Dados

### Mensagem de Registro MQTT
```json
{
  "device_id": "esp32-simulator",
  "ip": "192.168.1.100"
}
```
**Tópico:** `iot/register`

### Mensagem de Dados do Sensor MQTT
```json
{
  "device_id": "esp32-simulator",
  "sensor": "motor",
  "data": {
    "rpm": 1234.56,
    "temp": 28.5,
    "voltage": 12.3,
    "current": 2.7
  },
  "timestamp": "2025-11-16T15:30:45.123456"
}
```
**Tópico:** `iot/sensor/esp32-simulator`

### Confirmação do Servidor
```json
{
  "status": "registered",
  "device_id": "esp32-simulator",
  "ip": "192.168.1.100",
  "timestamp": "2025-11-16T15:30:40.123456"
}
```
**Tópico:** `iot/confirm/esp32-simulator`

---

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError"
```bash
# Instale as dependências faltantes
pip install requests paho-mqtt python-dotenv mysql-connector-python
```

### Erro: "Can't connect to MySQL server"
```bash
# Verifique se o MySQL está rodando
sudo systemctl status mysql

# Inicie se necessário
sudo systemctl start mysql

# Verifique as credenciais no arquivo .env
```

### Erro: "Connection refused" (MQTT)
```bash
# Verifique se o Mosquitto está rodando
sudo systemctl status mosquitto

# Inicie se necessário
sudo systemctl start mosquitto

# Teste a conexão
mosquitto_sub -h localhost -t "iot/#" -v
```

### Nenhum dado aparece no banco
1. Verifique se o servidor API está rodando
2. Verifique se o simulador se conectou ao MQTT
3. Verifique os logs do servidor API
4. Execute `test_database.py` para ver o estado atual

---

## 📊 Consultas SQL Úteis

```sql
-- Ver todas as ESPs
SELECT * FROM esps;

-- Ver todas as leituras com detalhes
SELECT 
    l.id,
    e.nome as esp,
    s.nome as sensor,
    l.timestamp
FROM leituras l
JOIN esps e ON l.esp_id = e.id
JOIN sensores s ON l.sensor_id = s.id
ORDER BY l.timestamp DESC
LIMIT 20;

-- Ver valores de uma leitura específica
SELECT campo, valor 
FROM valores 
WHERE leitura_id = 1;

-- Contar leituras por ESP
SELECT e.nome, COUNT(*) as total_leituras
FROM leituras l
JOIN esps e ON l.esp_id = e.id
GROUP BY e.nome;
```

---

## 📚 Arquivos Relacionados

- `../API/Server.py` - Servidor Flask principal
- `../API/mqtt_listener.py` - Listener MQTT que processa mensagens
- `../API/db_helper.py` - Funções de banco de dados
- `../Banco/CreateDB.sql` - Schema do banco
- `../Banco/InsertSensores.sql` - Dados iniciais dos sensores
- `../.env` - Configurações do ambiente
