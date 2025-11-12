#include "Sensor.h"

Sensor::Sensor(Pino* pinos, int numPinos, String name) {
    this->numPins = numPinos;
    this->name = name;
    this->pins = new Pino[numPinos];
    for(int i = 0; i < numPinos; i++) {
        this->pins[i] = pinos[i];
    }
}

Sensor::~Sensor() {
    delete[] pins;
}

String Sensor::toJSON() {
    JsonStore store;

    for (int i = 0; i < numPins; i++) {
        String key = "pin" + String(pins[i].getPin());
        store.setNumber(key, pins[i].read()); // Armazene o valor do pino
    }

    return store.toString();
}

JsonDocument Sensor::readValues() {
    JsonStore store;
    for (int i = 0; i < numPins; i++) {
        String key = "pin" + String(pins[i].getPin());
        store.setNumber(key, pins[i].read());
    }
    return store;
}