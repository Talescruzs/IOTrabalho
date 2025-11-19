#include "comunicacao.h"
#define encoder 13

bool dado = 0;
long tempo_ini = 0;
const int intervalo = 5000;


void setup() {
    pinMode(encoder, INPUT);
    comunicacaoInit("ESP2_RELE_ENCODER");
    Serial.begin(9600);
}

void loop() {
    comunicacaoTick();
    long tempo_atual = millis();
    bool novo_dado = digitalRead(encoder);
    if (tempo_atual - tempo_ini >= intervalo) {
        
        tempo_ini = tempo_atual;
    }
    if (novo_dado == HIGH && dado == LOW){
        JSONVar dados;
        dados["interrompido"] = true;
        enviarDadosSensor("encoder", dados);
        dado = novo_dado;
    } else if (novo_dado == LOW && dado == HIGH) {
        JSONVar dados;
        dados["interrompido"] = false;
        enviarDadosSensor("encoder", dados);
        dado = novo_dado;
    }
}
