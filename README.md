# IOTrabalho

## Divisao do trabalho
1. Dispositivos e sensores
    (futuro)
2. Comunicação e Transmissão
    Maria
3. Ingestão, Armazenamento e Processamento de Dados
    Bruna e Rafael
4. Aplicação / Visualização
    Tales e Pedro
5. Deploy e Testes
    (futuro)

## TODO List
- #### Dispositivos e sensores
- [ ] Fazer todos funcionarem

      - Sensor de Temperatura
      
      - Acelerômetro e Giroscópio

      - Sensor de Gestos e Cor

      - Sensor de Velocidade e Enconder

       - Distância Ultrassônico

      - Modulo Relé

      - Micro Motor de Vibração

      - Joystick

      - Teclado Matricial

      - Controle Remoto Ir + Receptor Ir

      - Umidade e Temperatura
      
- #### Comunicação e Transmissão
- [ ] Definir estrutura de pre processamento
- [x] Definir protocolo de comunicacao
- #### Ingestão, Armazenamento e Processamento de Dados (pre processamento)
- [ ] Organizar as bibliotecas dos sensores
- [ ] Organizar os dados em um buffer
- #### Aplicação / Visualização
- [ ] Recebimento dos dados (passivo)
- [ ] Tratamento dos dados 
- [x] Definir banco 
- [x] Armazenamento dos dados 
- [ ] Criacao de dashboard 
- [ ] API para disponibilizacao dos dados 
- #### Deploy e Testes
- [ ] Funcionar 
- [ ] Dominar o mundo  


## Documentacao
### O que e o projeto?
Plataforma para tratamento de dados de sensores

#### Falta ou nao funciona
- encoder



### Mecanica
- Base e carenagem impressas
- Parafusos
- protoboard pequena



## Onde ouvir a comunicação da ESP32
A ESP32 sobe um servidor HTTP na porta 80 (definido em `comunicacao.ino`) e expõe o endpoint `/status`.

Como descobrir o IP:
1. Abra o Serial Monitor após o boot da ESP32.
2. Procure pela linha: `Endereço de IP:` e anote o IP mostrado (ex.: `192.168.0.50`).

Escutar direto na ESP32:
- Navegador: `http://<IP_DA_ESP>/status`
- curl:
  ```
  curl http://<IP_DA_ESP>/status
  ```

Escutar via API (proxy):
- Endpoint: `GET http://127.0.0.1:5000/esp/status?host=<IP_DA_ESP>`
- Exemplo:
  ```
  curl "http://127.0.0.1:5000/esp/status?host=192.168.0.50"
  ```
- Opcional: defina a variável de ambiente `ESP32_HOST` e chame sem `host`:
  ```
  export ESP32_HOST=192.168.0.50
  curl http://127.0.0.1:5000/esp/status
  ```

O payload esperado é um JSON montado na ESP32 contendo `device`, `sensor`, `data` e `ts`.