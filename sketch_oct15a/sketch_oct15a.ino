#include "JsonStore.h"

JsonStore jsonStore;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  // Inicializa o objeto JSON com alguns campos
  jsonStore.set("device", "carro");
  jsonStore.set("status", "idle");
  JSONVar v; v = 0;
  jsonStore.setNested("sensors", "rpm", v);
  v = 0; jsonStore.setNested("sensors", "temp", v);
}

void loop() {
  // Atualiza periodicamente um valor e imprime o JSON completo
  static unsigned long last = 0;
  static int rpm = 0;
  if (millis() - last >= 1000) {
    rpm = (rpm + 100) % 4000; // valor simulado
    JSONVar v; v = rpm;
    jsonStore.setNested("sensors", "rpm", v);
    jsonStore.setNumber("timestamp", millis());

    Serial.println(jsonStore.toString());
    last = millis();
  }
}
