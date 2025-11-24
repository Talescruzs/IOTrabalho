#include "comunicacao.h"

#define VERDE 15
#define AMARELO 13
#define VERMELHO 12

/*
 * recebe:
 *      ["pisca"] = 1 (vermelho), 2 (verde) ou 3 (amarelo)
 *      ["alerta"] = boolean;
*/


void processarComando(const String& command, const JSONVar& params) {
    if (command == "pisca") {
        if (params.hasOwnProperty("pisca")) {
            int retornoValue = (int)params["pisca"];

            if (retornoValue == 1) {
                digitalWrite(VERMELHO, HIGH);
            } else if (retornoValue == 2) {
                digitalWrite(VERDE, HIGH);
            } else if (retornoValue == 3) {
                digitalWrite(AMARELO, HIGH);
            }
            delay(3000);

            if (retornoValue == 1) {
                digitalWrite(VERMELHO, LOW);
            } else if (retornoValue == 2) {
                digitalWrite(VERDE, LOW);
            } else if (retornoValue == 3) {
                digitalWrite(AMARELO, LOW);
            }
        }
    }
    else if (command == "alerta") {
        int retornoValue = (int)params["alerta"];
    
        if (retornoValue) {
            digitalWrite(VERMELHO, HIGH);
            digitalWrite(VERDE, HIGH);
        } else if (!retornoValue) {
            digitalWrite(VERMELHO, LOW);
            digitalWrite(VERDE, LOW);
        }
    }
    else {
        Serial.println("Comando desconhecido: " + command);
    }
}

void setup() {
    Serial.begin(9600);
    comunicacaoInit("ESP32_LEDS");
    comunicacaoSetCallback(processarComando);
    pinMode(VERDE, OUTPUT);
    pinMode(AMARELO, OUTPUT);
    pinMode(VERMELHO, OUTPUT);
    digitalWrite(VERDE, LOW);
    digitalWrite(VERMELHO, LOW);
    digitalWrite(AMARELO, LOW);
}

void loop(){
    comunicacaoTick();
}