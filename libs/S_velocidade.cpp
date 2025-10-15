#include "S_velocidade.h"

Encoder::Encoder(int encoder)
{
    pino = encoder;
    pinMode(encoder, INPUT);  
}

Encoder::medirRPM() {
    tempo_inicial = micros();
    unsigned long t = tempo_inicial - tempo_final;
    if (t >= 1000000) {
        RPM = 60 / ((1000000) * t * qtd_buracos);
        tempo_final = tempo_inicial;
    }
}

Encoder::getRPM(){
    return RPM;
}

//attachInterrupt(digitalPinToInterrupt(encoder), medirRPM, RISING);
