#include "comunicacao.h"
#include <Arduino_JSON.h>

#define encoder 13
#define rele 12

/*
 *  recebe: 
 *       destravar = boolean; true se a senha foi correta
 *  envia:
 *      ["alerta"] = boolean; true se deu timeout (porta aberta por > 5 segundos)
 *      ["portal_aberta"] = boolean; true se a porta abriu (está interrompendo o sensor)
*/

bool dado = LOW;
long tempo_ini = 0;
const int intervalo = 5000;

void processarComando(const String& command, const JSONVar& params) {
  if (command == "destravar") {
    if (params.hasOwnProperty("destravar")) {
      bool retornoValue = (bool)params["destravar"];
      
      if (retornoValue == true) {
        digitalWrite(rele, HIGH);
      }
    }
  }
  else {
    Serial.println("Comando desconhecido: " + command);
  }
}

void setup() {
    pinMode(encoder, INPUT);
    pinMode(rele, OUTPUT);
    comunicacaoInit("ESP32_DOOR");
    comunicacaoSetCallback(processarComando);
    Serial.begin(9600);
}

void loop() {
    comunicacaoTick();
    long tempo_atual = millis();
    bool novo_dado = !digitalRead(encoder);
    if (tempo_atual - tempo_ini >= intervalo) {
        if (dado == LOW) {
            JSONVar dados;
            dados["alerta"] = true;
            dados["porta_aberta"] = true;
            enviarDadosSensor("encoder", dados);
        }
        tempo_ini = tempo_atual;
    }
    if (novo_dado == HIGH && dado == LOW){
        JSONVar dados;
        dados["porta_aberta"] = false;
        dados["alerta"] = false;
        enviarDadosSensor("encoder", dados);
        digitalWrite(rele, LOW);
        dado = novo_dado;
    } else if (novo_dado == LOW && dado == HIGH) {
        JSONVar dados;
        dados["porta_aberta"] = true;
        dados["alerta"] = false;
        enviarDadosSensor("encoder", dados);
        dado = novo_dado;
    }
}
