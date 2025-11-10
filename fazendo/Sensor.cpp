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
    StaticJsonDocument<200> doc;
    
    JsonArray pinsArray = doc.createNestedArray("pins");
    for(size_t i = 0; i < numPins; i++) {
        JsonObject pinObj = pinsArray.createNestedObject();
        pinObj["value"] = pins[i].read();
    }
    
    String output;
    serializeJson(doc, output);
    return output;
}

JsonDocument Sensor::readValues() {
    StaticJsonDocument<200> doc;
    
    for(size_t i = 0; i < numPins; i++) {
        doc[String("pin") + String(pins[i].getPin())] = pins[i].read();
    }
    
    return doc;
}