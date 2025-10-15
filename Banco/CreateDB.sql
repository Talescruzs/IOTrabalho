CREATE TABLE sensores (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(50)
);

CREATE TABLE leituras (
    id SERIAL PRIMARY KEY,
    sensor_id INTEGER REFERENCES sensores(id),
    valor FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);