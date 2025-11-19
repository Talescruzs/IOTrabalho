-- Nota: SQLite não suporta CREATE DATABASE. O banco é criado automaticamente ao conectar.
-- Se precisar de múltiplos bancos, use arquivos .db separados.
-- Para PostgreSQL/MySQL, descomente a linha abaixo:
CREATE DATABASE IF NOT EXISTS ioTabelas;

USE ioTabelas;

CREATE TABLE IF NOT EXISTS sensores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS esps (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50) NOT NULL UNIQUE,
    ip_address VARCHAR(15)
);

-- Insere ESP padrão/desconhecida (ID=1) para leituras sem ESP específica
INSERT IGNORE INTO esps (id, nome, ip_address) VALUES (1, 'unknown', NULL);

CREATE TABLE IF NOT EXISTS leituras (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_id INT NOT NULL,
    esp_id INT NOT NULL DEFAULT 1,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sensor_id) REFERENCES sensores(id) ON DELETE CASCADE,
    FOREIGN KEY (esp_id) REFERENCES esps(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS valores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    leitura_id INT NOT NULL,
    campo VARCHAR(50) NOT NULL,
    valor FLOAT NOT NULL,
    FOREIGN KEY (leitura_id) REFERENCES leituras(id) ON DELETE CASCADE
);

-- Índices para performance (usando sintaxe compatível com MySQL)
-- Nota: MySQL não suporta IF NOT EXISTS em índices
-- Erros de duplicação são ignorados no código Python
CREATE INDEX idx_leituras_sensor ON leituras(sensor_id);
CREATE INDEX idx_leituras_timestamp ON leituras(timestamp);
CREATE INDEX idx_valores_leitura ON valores(leitura_id);