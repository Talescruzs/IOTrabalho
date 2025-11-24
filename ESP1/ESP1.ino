
#include "comunicacao.h"
#include <Keypad.h>
#include <Arduino_JSON.h>

#define PIN_VIBRA 21  

/*
 *  recebe:
 *          ["autorizado"] = boolean; true se a senha estiver correta
 *
 *  envia:
 *          ["senha"] = string; senha digitada pelo usuário
 *
 *  comportamento:
 *      - 4 digitos digitados
 *      - Pressiona '#' para enviar
 *      - Pressiona '*' para limpar
 */


const byte ROWS = 4; 
const byte COLS = 4;

char keys[ROWS][COLS] = {
  {'1','2','3','A'},
  {'4','5','6','B'},
  {'7','8','9','C'},
  {'*','0','#','D'}
};

byte rowPins[ROWS] = {32, 33, 25, 26};

byte colPins[COLS] = {2, 15, 13, 12};

Keypad keypad = Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);

String senha_digitada = "";
const int SENHA_TAM = 4;

void processarComando(const String& command, const JSONVar& params) {
    Serial.println("Comando recebido: " + command);

    if (command == "resultado") {
        if (params.hasOwnProperty("autorizado")) {
            bool ok = (bool)params["autorizado"];

            if (ok) {
                Serial.println("ACESSO AUTORIZADO");
                digitalWrite(PIN_VIBRA, HIGH);
                delay(300);  
                digitalWrite(PIN_VIBRA, LOW);
            } else {
                Serial.println("ACESSO NEGADO");
                for (int i = 0; i < 3; i++) {
                    digitalWrite(PIN_VIBRA, HIGH);
                    delay(120);
                    digitalWrite(PIN_VIBRA, LOW);
                    delay(60);
                }
            }
        }
    }
}

void enviarSenha(String senha) {
    JSONVar data;
    data["senha"] = senha;

    Serial.println("Enviando senha: " + senha);
    enviarDadosSensor("keypad", data);
}

void setup() {
    Serial.begin(9600);
    pinMode(PIN_VIBRA, OUTPUT);

    comunicacaoInit("ESP1_KEYPAD");
    comunicacaoSetCallback(processarComando);

    Serial.println("ESP1 iniciado");
}

void loop() {
    comunicacaoTick();

    char tecla = keypad.getKey();

    if (tecla) {
        Serial.print("Tecla: ");
        Serial.println(tecla);

        if (tecla == '*') {
            senha_digitada = "";
            Serial.println("Senha apagada");
            return;
        }

        if (tecla == '#') {
            if (senha_digitada.length() == SENHA_TAM) {
                enviarSenha(senha_digitada);
            } else {
                Serial.println("Senha incompleta");
            }
            senha_digitada = "";
            return;
        }

        if (senha_digitada.length() < SENHA_TAM && isDigit(tecla)) {
            senha_digitada += tecla;
        }
    }
}
