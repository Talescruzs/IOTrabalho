-- Inserts dos sensores do projeto IoT
-- Data: 16/11/2025

USE ioTabelas;

-- Limpa dados anteriores se necessário (comentado por segurança)
-- DELETE FROM valores;
-- DELETE FROM leituras;
-- DELETE FROM sensores;
-- ALTER TABLE sensores AUTO_INCREMENT = 1;

-- Inserção dos sensores
INSERT INTO sensores (nome) VALUES 
    ('DS18B20'),                    -- Sensor de Temperatura
    ('MPU-6050'),                   -- Acelerômetro e Giroscópio
    ('APDS-9960'),                  -- Sensor de Gestos e Cor
    ('Encoder'),                    -- Sensor de Velocidade Encoder
    ('HC-SR04'),                    -- Sensor de Distância Ultrassônico
    ('Relé JQC3F'),                 -- Módulo Relé 5V 10A 1 Canal
    ('Motor Vibração'),             -- Micro Motor de Vibração
    ('KY023'),                      -- Joystick 3 Eixos
    ('Teclado 4x4'),                -- Teclado Matricial Membrana
    ('Controle IR'),                -- Controle Remoto IR + Receptor
    ('DHT11');                      -- Sensor de Umidade e Temperatura

-- Verifica inserção
SELECT * FROM sensores;

-- Exemplos de como seria uma leitura completa para cada sensor:

-- Exemplo 1: Leitura do DS18B20 (Temperatura)
-- INSERT INTO leituras (sensor_id) VALUES (1);
-- INSERT INTO valores (leitura_id, campo, valor) VALUES 
--     (LAST_INSERT_ID(), 'temperatura', 25.5);

-- Exemplo 2: Leitura do MPU-6050 (Acelerômetro e Giroscópio)
-- INSERT INTO leituras (sensor_id) VALUES (2);
-- INSERT INTO valores (leitura_id, campo, valor) VALUES 
--     (LAST_INSERT_ID(), 'accel_x', 0.15),
--     (LAST_INSERT_ID(), 'accel_y', -0.02),
--     (LAST_INSERT_ID(), 'accel_z', 9.81),
--     (LAST_INSERT_ID(), 'gyro_x', 0.5),
--     (LAST_INSERT_ID(), 'gyro_y', -0.3),
--     (LAST_INSERT_ID(), 'gyro_z', 0.1);

-- Exemplo 3: Leitura do APDS-9960 (Gestos e Cor)
-- INSERT INTO leituras (sensor_id) VALUES (3);
-- INSERT INTO valores (leitura_id, campo, valor) VALUES 
--     (LAST_INSERT_ID(), 'red', 120),
--     (LAST_INSERT_ID(), 'green', 85),
--     (LAST_INSERT_ID(), 'blue', 200),
--     (LAST_INSERT_ID(), 'clear', 405),
--     (LAST_INSERT_ID(), 'proximity', 50),
--     (LAST_INSERT_ID(), 'gesture', 1);  -- 1=UP, 2=DOWN, 3=LEFT, 4=RIGHT

-- Exemplo 4: Leitura do Encoder (Velocidade)
-- INSERT INTO leituras (sensor_id) VALUES (4);
-- INSERT INTO valores (leitura_id, campo, valor) VALUES 
--     (LAST_INSERT_ID(), 'rpm', 1500),
--     (LAST_INSERT_ID(), 'pulsos', 24);

-- Exemplo 5: Leitura do HC-SR04 (Distância)
-- INSERT INTO leituras (sensor_id) VALUES (5);
-- INSERT INTO valores (leitura_id, campo, valor) VALUES 
--     (LAST_INSERT_ID(), 'distancia_cm', 45.3);

-- Exemplo 6: Estado do Relé
-- INSERT INTO leituras (sensor_id) VALUES (6);
-- INSERT INTO valores (leitura_id, campo, valor) VALUES 
--     (LAST_INSERT_ID(), 'estado', 1);  -- 0=OFF, 1=ON

-- Exemplo 7: Estado do Motor de Vibração
-- INSERT INTO leituras (sensor_id) VALUES (7);
-- INSERT INTO valores (leitura_id, campo, valor) VALUES 
--     (LAST_INSERT_ID(), 'intensidade', 75);  -- 0-100%

-- Exemplo 8: Leitura do Joystick KY023
-- INSERT INTO leituras (sensor_id) VALUES (8);
-- INSERT INTO valores (leitura_id, campo, valor) VALUES 
--     (LAST_INSERT_ID(), 'eixo_x', 512),
--     (LAST_INSERT_ID(), 'eixo_y', 480),
--     (LAST_INSERT_ID(), 'botao', 0);  -- 0=não pressionado, 1=pressionado

-- Exemplo 9: Leitura do Teclado Matricial
-- INSERT INTO leituras (sensor_id) VALUES (9);
-- INSERT INTO valores (leitura_id, campo, valor) VALUES 
--     (LAST_INSERT_ID(), 'tecla', 5);  -- Código da tecla pressionada

-- Exemplo 10: Leitura do Controle IR
-- INSERT INTO leituras (sensor_id) VALUES (10);
-- INSERT INTO valores (leitura_id, campo, valor) VALUES 
--     (LAST_INSERT_ID(), 'codigo', 16753245);  -- Código IR recebido

-- Exemplo 11: Leitura do DHT11 (Umidade e Temperatura)
-- INSERT INTO leituras (sensor_id) VALUES (11);
-- INSERT INTO valores (leitura_id, campo, valor) VALUES 
--     (LAST_INSERT_ID(), 'temperatura', 26.0),
--     (LAST_INSERT_ID(), 'umidade', 65.0);
