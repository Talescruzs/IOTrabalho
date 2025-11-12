#ifndef SENSOR_H
#define SENSOR_H

#include <ArduinJson.h>
#include <Arduino.h>
#include "Pino.h"
#include "JsonStore.h"

class Sensor
{
private:
    Pino* pins;
    int numPins;
    String name;
public:
    Sensor(Pino* pinos, int numPinos, String name);
    ~Sensor();
    String toJson();
    JsonDocument readValues();
};

#endif
