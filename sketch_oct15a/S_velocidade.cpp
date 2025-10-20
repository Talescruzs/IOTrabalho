#include "S_velocidade.h"

unsigned long tempo_final=0;
unsigned int RPM = 0;
int qtd_buracos = 1;

void medirRPM() {
    unsigned long tempo_inicial = micros();
    unsigned long t = tempo_inicial - tempo_final;
    if (t >= 1000000) {
        RPM = 60 / ((1000000) * t * qtd_buracos);
        tempo_final = tempo_inicial;
    }
}
/*
    * Precisa usar no setup() a seguinte função:
    * attachInterrupt(digitalPinToInterrupt(encoder), medirRPM, RISING);
    * E esse código todo é pura gambiarra...
    * Boa sorte!
*/
