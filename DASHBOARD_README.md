# 📊 Dashboard IoT - Guia de Uso

## 🚀 Iniciando o Sistema

### 1. Iniciar o Servidor API
```bash
cd /home/vboxuser/repos/IOTrabalho
.venv/bin/python API/Server.py
```

O servidor estará disponível em: `http://localhost:5000`

### 2. Iniciar o Simulador ESP32 (opcional)
```bash
.venv/bin/python Testes/simulate_esp32.py
```

Isso enviará dados simulados para popular o dashboard com informações.

---

## 📺 Acessando o Dashboard

### URLs Disponíveis:

1. **Dashboard de Gráficos**: `http://localhost:5000/dashboard`
   - Visualização completa dos dados em gráficos interativos
   - Atualização automática a cada 10 segundos
   
2. **Controle do Carrinho**: `http://localhost:5000/`
   - Interface de controle via teclado

---

## 📊 Funcionalidades do Dashboard

### 1. Estatísticas em Tempo Real
- **Total de ESPs**: Quantidade de dispositivos ESP32 registrados
- **Total de Sensores**: Quantidade de sensores cadastrados no sistema
- **Total de Leituras**: Número de registros salvos no banco de dados
- **Status do Sistema**: Indicador de conectividade com a API

### 2. Gráficos Disponíveis

#### 📈 Leituras por ESP
- Gráfico de barras mostrando quantidade de leituras por dispositivo
- Identifica quais ESPs estão mais ativas

#### 📊 Leituras por Sensor
- Gráfico de pizza (donut) mostrando distribuição por tipo de sensor
- Visualiza proporção de uso de cada sensor

#### ⏱️ Timeline de Leituras
- Gráfico de linha temporal das últimas 100 leituras
- Mostra atividade ao longo do tempo
- Cada sensor tem sua própria linha colorida

### 3. Tabela de Valores Recentes
- Lista os últimos valores lidos de cada sensor
- Mostra timestamp de cada leitura
- Valores formatados e coloridos para fácil visualização

---

## 🔄 Atualização de Dados

### Automática
- O dashboard atualiza automaticamente a cada **10 segundos**
- Não é necessário recarregar a página

### Manual
- Clique no botão **"🔄 Atualizar Dados"** no topo da página
- Força uma atualização imediata

---

## 🎨 Gráficos Interativos

Os gráficos utilizam **Chart.js** e oferecem:

✅ Hover para ver detalhes  
✅ Legenda clicável para filtrar dados  
✅ Responsivos (adaptam ao tamanho da tela)  
✅ Animações suaves  

---

## 📡 Endpoints da API

### Dados para Gráficos
```bash
GET http://localhost:5000/api/chart-data
```

**Retorna:**
```json
{
  "ok": true,
  "data": {
    "leituras_por_esp": [
      {"esp": "esp32-simulator", "total_leituras": 25}
    ],
    "leituras_por_sensor": [
      {"sensor": "motor", "total_leituras": 25}
    ],
    "ultimas_leituras": [...],
    "valores_recentes": [...]
  }
}
```

### Histórico de Sensor Específico
```bash
GET http://localhost:5000/api/sensor-history?sensor=motor&limit=50
```

**Parâmetros:**
- `sensor` (obrigatório): Nome do sensor
- `limit` (opcional): Quantidade de registros (padrão: 50)

---

## 🧪 Testando o Sistema Completo

### Passo 1: Preparar o Banco
```bash
# Se necessário, criar o banco
mysql -u tales -psenha123 < Banco/CreateDB.sql

# Popular com sensores
mysql -u tales -psenha123 ioTabelas < Banco/InsertSensores.sql
```

### Passo 2: Verificar Dados
```bash
.venv/bin/python Testes/test_database.py --all
```

### Passo 3: Iniciar Servidor
```bash
.venv/bin/python API/Server.py
```

Saída esperada:
```
✓ Variáveis carregadas de /home/vboxuser/repos/IOTrabalho/.env
[config] MQTT_BROKER=localhost, MQTT_PORT=1883, MQTT_TOPIC=iot/register
Conectando ao MySQL: tales@localhost:3306
✓ Banco MySQL inicializado.
[mqtt] listener iniciado em thread daemon (broker=localhost:1883)
CORS habilitado para todos os origins.
 * Running on http://0.0.0.0:5000
```

### Passo 4: Gerar Dados de Teste
Em outro terminal:
```bash
.venv/bin/python Testes/simulate_esp32.py
```

Aguarde alguns segundos para o simulador enviar dados.

### Passo 5: Acessar Dashboard
Abra no navegador: `http://localhost:5000/dashboard`

---

## 📱 Screenshots das Funcionalidades

### Estatísticas no Topo
```
┌─────────────────────────────────────────────────────────┐
│ Total de ESPs         Total de Sensores                 │
│      2                     11                            │
│                                                          │
│ Total de Leituras     Status                            │
│      45               🟢 Online                          │
└─────────────────────────────────────────────────────────┘
```

### Gráficos
```
┌──────────────────────┐  ┌──────────────────────┐
│ Leituras por ESP     │  │ Leituras por Sensor  │
│                      │  │                      │
│  [Gráfico de Barras] │  │  [Gráfico de Pizza]  │
│                      │  │                      │
└──────────────────────┘  └──────────────────────┘
```

### Tabela de Valores
```
┌────────────────────────────────────────────────────────┐
│ Sensor  │ Campos                │ Valores  │ Timestamp │
├─────────┼──────────────────────┼──────────┼───────────┤
│ motor   │ rpm, temp, voltage,  │ rpm: ... │ 16:45:23  │
│         │ current              │ temp:... │           │
└────────────────────────────────────────────────────────┘
```

---

## 🎯 Personalizações Possíveis

### Alterar Intervalo de Atualização
Edite `dashboard.html`, linha final:
```javascript
// Mude de 10000 (10s) para o valor desejado em milissegundos
setInterval(loadAllData, 10000);
```

### Adicionar Novos Gráficos
1. Adicione endpoint em `API/controllers.py`
2. Adicione rota em `API/routes.py`
3. Adicione função JavaScript em `dashboard.html`
4. Adicione canvas no HTML

### Mudar Cores dos Gráficos
Edite o array `colors` na função `updateChartSensores()`:
```javascript
const colors = [
    '#667eea',  // Roxo
    '#764ba2',  // Roxo escuro
    '#f093fb',  // Rosa
    // ... adicione mais cores
];
```

---

## 🐛 Troubleshooting

### Dashboard não carrega dados
1. Verifique se o servidor está rodando: `http://localhost:5000/api/chart-data`
2. Abra o console do navegador (F12) e veja erros
3. Verifique se há dados no banco: `.venv/bin/python Testes/test_database.py`

### Gráficos não aparecem
1. Verifique conexão com internet (Chart.js vem de CDN)
2. Verifique console do navegador por erros JavaScript
3. Tente recarregar a página (Ctrl+F5)

### Erro "db_helper não disponível"
```bash
# Instale o conector MySQL
pip install mysql-connector-python
```

### Erro de conexão com banco
1. Verifique se MySQL está rodando: `sudo systemctl status mysql`
2. Verifique credenciais no `.env`
3. Teste conexão: `.venv/bin/python Testes/test_database.py`

---

## 📚 Tecnologias Utilizadas

- **Backend**: Flask (Python)
- **Banco de Dados**: MySQL
- **Frontend**: HTML5, CSS3, JavaScript
- **Gráficos**: Chart.js 4.4.0
- **MQTT**: Paho-MQTT (Python)

---

## 🔗 Links Úteis

- Chart.js Docs: https://www.chartjs.org/docs/latest/
- Flask Docs: https://flask.palletsprojects.com/
- MySQL Connector: https://dev.mysql.com/doc/connector-python/en/

---

## 📝 Notas

- O dashboard funciona melhor em navegadores modernos (Chrome, Firefox, Edge)
- Recomendado tela com resolução mínima de 1280x720
- Para produção, considere usar HTTPS e autenticação
