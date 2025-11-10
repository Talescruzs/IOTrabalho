#include <Arduino.h>
#include <Pino.h>

Pino::Pino(int pin, int mode, int type, bool pwm)
{
    this->pin = pin;
    this->mode = mode;
    this->type = type;
    this->PWM = pwm;
    pinMode(pin, mode);
}

int Pino::getPin() {
    return pin;
}

int Pino::read(){
    if (mode != INPUT && mode != INPUT_PULLUP) return -1;
    if (type == ANALOGICO) return analogRead(pin);
    else return digitalRead(pin);
}

bool Pino::write(int data){
    if (mode != OUTPUT) return false;
    if (type == ANALOGICO || PMW) {
        analogWrite(pin, data);
        return true;
    }
    else {
        digitalWrite(pin, data ? HIGH : LOW);
        return true;
    }
}

Pino::~Pino()
{
}
