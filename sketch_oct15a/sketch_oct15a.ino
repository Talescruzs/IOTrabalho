#include "comunicacao.h"

void setup() {
  comunicacaoInit("ESP32_LAB_001");  // Conecta WiFi e MQTT com nome personalizado
  
}

void loop() {
  comunicacaoTick();  // Mantém conexões ativas
  
  // Exemplo: Enviar dados de sensor periodicamente
  static unsigned long lastSend = 0;
  if (millis() - lastSend > 10000) {  // A cada 10 segundos
    JSONVar dados;
    dados["rpm"] = random(1000, 4000);
    dados["temp"] = random(20, 45);
    dados["voltage"] = 12.0;
    dados["current"] = 2.5;
    
    enviarDadosSensor("motor", dados);
    
    lastSend = millis();
  }
  
  delay(10);
}