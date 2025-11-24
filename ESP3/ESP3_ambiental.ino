#include <Arduino.h>
#include "DHT.h"
#include "comunicacao.h"
#include "ESP3_ambiental.h"

#define DHTPIN 15
#define DHTTYPE DHT11

/*
 *  envia:
 *      ["temperatura"] = float; valor em °C lido do DHT11
 *      ["umidade"] = float; valor em % lido do DHT11
 *
 */

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  dht.begin();

  comunicacaoInit("ESP3_AMBIENTAL");

  Serial.println("\nESP3 Ambiental iniciado");
  Serial.println("Aguardando comandos...\n");
}


void loop() {
  comunicacaoTick(); 

  static unsigned long lastSend = 0;
  unsigned long now = millis();

  if (now - lastSend >= 1000) {
    float humidity = dht.readHumidity();
    float temperature = dht.readTemperature();

    if (isnan(humidity) || isnan(temperature)) {
      Serial.println("Erro ao ler DHT11");
      lastSend = now; 
    } else {
      Serial.print("Temp: ");
      Serial.print(temperature);
      Serial.print(" °C | Umidade: ");
      Serial.print(humidity);
      Serial.println(" %");

      JSONVar dados;
      dados["temperatura"] = temperature;
      dados["umidade"] = humidity;

      enviarDadosSensor("ambiental", dados);
      lastSend = now;
    }
  }
}
