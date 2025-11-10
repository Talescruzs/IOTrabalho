#ifndef PINO_H
#define PINO_H

#include <Arduino.h>

#define ANALOGICO 1
#define DIGITAL 0

class Pino {
private:
    int pin;
    int mode;
    int type;
    bool PWM;

public:
    Pino(int pin, int mode, int type, bool pwm);
    ~Pino();
    int getPin();
    int read();
    bool write(int data);
};

#endif
