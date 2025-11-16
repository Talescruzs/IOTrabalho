# 🗄️ Scripts de Gerenciamento do Banco de Dados

Este diretório contém scripts para criar, popular e excluir o banco de dados IoT.

## 📋 Arquivos Disponíveis

### 1. `CreateDB.sql` - Criar Banco de Dados
Cria o banco `ioTabelas` e todas as tabelas necessárias.

**Uso via MySQL:**
```bash
mysql -u tales -psenha123 < Banco/CreateDB.sql
```

**O que cria:**
- ✅ Banco de dados `ioTabelas`
- ✅ Tabela `sensores` - cadastro de sensores
- ✅ Tabela `esps` - dispositivos ESP32 registrados
- ✅ Tabela `leituras` - registros de leituras dos sensores
- ✅ Tabela `valores` - valores individuais de cada leitura
- ✅ Índices para melhor performance
- ✅ ESP padrão (ID=1, nome='unknown')

---

### 2. `InsertSensores.sql` - Popular Sensores
Insere os 11 sensores do projeto no banco.

**Uso:**
```bash
mysql -u tales -psenha123 ioTabelas < Banco/InsertSensores.sql
```

**Sensores incluídos:**
1. DS18B20 (Temperatura)
2. MPU-6050 (Acelerômetro e Giroscópio)
3. APDS-9960 (Gestos e Cor)
4. Encoder (Velocidade)
5. HC-SR04 (Distância Ultrassônica)
6. Relé JQC3F
7. Motor Vibração
8. KY023 (Joystick 3 Eixos)
9. Teclado 4x4
10. Controle IR
11. DHT11 (Umidade e Temperatura)

---

### 3. `DropDB.sql` - Excluir Banco (SQL)
⚠️ **PERIGO:** Exclui permanentemente o banco `ioTabelas` e todos os dados.

**Uso:**
```bash
mysql -u tales -psenha123 < Banco/DropDB.sql
```

---

### 4. `drop_db.py` - Excluir Banco (Python Interativo)
⚠️ **PERIGO:** Script Python interativo que solicita confirmação antes de excluir.

**Uso:**
```bash
# Com ambiente virtual ativado
python Banco/drop_db.py

# Ou diretamente
.venv/bin/python Banco/drop_db.py
```

**Características:**
- ✅ Solicita dupla confirmação
- ✅ Verifica se o banco existe
- ✅ Exibe mensagens claras de aviso
- ✅ Usa configurações do `.env`

**Exemplo de uso:**
```
============================================================
EXCLUIR BANCO DE DADOS IOT
============================================================
Host: localhost
Porta: 3306
Banco: ioTabelas
============================================================

⚠️  ATENÇÃO: Esta ação irá APAGAR TODOS OS DADOS!
⚠️  Esta operação NÃO PODE ser desfeita!

Digite 'EXCLUIR' para confirmar a exclusão do banco 'ioTabelas': EXCLUIR

Tem CERTEZA ABSOLUTA? Digite novamente 'ioTabelas': ioTabelas

🗑️  Excluindo banco de dados...

✓ Banco 'ioTabelas' excluído com sucesso!
✓ Todos os dados foram permanentemente removidos.
```

---

### 5. `init_db.py` - Inicialização via Python
Script Python para criar o banco de dados programaticamente.

**Uso:**
```bash
python Banco/init_db.py
```

---

## 🚀 Fluxo Completo de Uso

### Primeira Instalação

```bash
# 1. Criar o banco e tabelas
mysql -u tales -psenha123 < Banco/CreateDB.sql

# 2. Popular com os sensores
mysql -u tales -psenha123 ioTabelas < Banco/InsertSensores.sql

# 3. Verificar se está tudo OK
.venv/bin/python Testes/test_database.py
```

### Resetar o Banco (Limpar Dados)

```bash
# Opção 1: Via SQL (direto)
mysql -u tales -psenha123 < Banco/DropDB.sql
mysql -u tales -psenha123 < Banco/CreateDB.sql
mysql -u tales -psenha123 ioTabelas < Banco/InsertSensores.sql

# Opção 2: Via Python (com confirmação)
.venv/bin/python Banco/drop_db.py
mysql -u tales -psenha123 < Banco/CreateDB.sql
mysql -u tales -psenha123 ioTabelas < Banco/InsertSensores.sql
```

### Limpar Apenas os Dados (Manter Estrutura)

```sql
-- Conectar ao MySQL
mysql -u tales -psenha123 ioTabelas

-- Limpar dados mantendo estrutura
DELETE FROM valores;
DELETE FROM leituras;
DELETE FROM esps WHERE id > 1;  -- Mantém ESP 'unknown'
DELETE FROM sensores;

-- Repopular sensores
SOURCE Banco/InsertSensores.sql;
```

---

## 📊 Estrutura das Tabelas

### `sensores`
```sql
id          INT AUTO_INCREMENT PRIMARY KEY
nome        VARCHAR(50) NOT NULL
```

### `esps`
```sql
id          INT AUTO_INCREMENT PRIMARY KEY
nome        VARCHAR(50) NOT NULL UNIQUE
ip_address  VARCHAR(15)
```

### `leituras`
```sql
id          INT AUTO_INCREMENT PRIMARY KEY
sensor_id   INT NOT NULL (FK -> sensores.id)
esp_id      INT NOT NULL DEFAULT 1 (FK -> esps.id)
timestamp   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

### `valores`
```sql
id          INT AUTO_INCREMENT PRIMARY KEY
leitura_id  INT NOT NULL (FK -> leituras.id)
campo       VARCHAR(50) NOT NULL
valor       FLOAT NOT NULL
```

---

## ⚠️ Avisos Importantes

1. **Backup antes de dropar:**
   ```bash
   mysqldump -u tales -psenha123 ioTabelas > backup_ioTabelas_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **Restaurar de backup:**
   ```bash
   mysql -u tales -psenha123 ioTabelas < backup_ioTabelas_20251116_153045.sql
   ```

3. **Verificar dados antes de dropar:**
   ```bash
   .venv/bin/python Testes/test_database.py
   ```

---

## 🔧 Troubleshooting

### Erro: "Access denied"
```bash
# Verifique as credenciais no arquivo .env
cat ../.env | grep DB_
```

### Erro: "Database doesn't exist"
```bash
# Crie o banco primeiro
mysql -u tales -psenha123 < Banco/CreateDB.sql
```

### Ver todas as tabelas
```bash
mysql -u tales -psenha123 -e "SHOW TABLES FROM ioTabelas;"
```

### Ver estrutura de uma tabela
```bash
mysql -u tales -psenha123 -e "DESCRIBE ioTabelas.leituras;"
```

---

## 📚 Ordem de Criação Recomendada

1. `CreateDB.sql` - Cria banco e estrutura
2. `InsertSensores.sql` - Popula sensores
3. Iniciar aplicação - ESPs se registram automaticamente via MQTT
4. Dados são inseridos automaticamente conforme recebidos
