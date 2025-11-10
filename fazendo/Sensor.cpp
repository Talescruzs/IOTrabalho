#include <Arduino.h>
#include <Pino.h>

class Sensor
{
private:
    Pino[] pins;
public:
    Sensor(Pino[] pinos);
    ~Sensor();
};

Sensor::Sensor(Pino[] pinos)
{
    this->pinos = pinos;
}

Sensor::~Sensor()
{
}
