#ifndef SENSOR_V_H
#define SENSOR_V_H

class Encoder
{
private:
    int pino;
    int qtd_buracos;
    unsigned long tempo_inicial;
    unsigned long tempo_final;
    uint8_t RPM;
    unsigned int medirRPM();
public:
    Encoder(int encoder);
    unsigned int getRPM();
};

#endif