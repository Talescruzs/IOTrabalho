#include <WiFi.h>
#include <Arduino_JSON.h>

char* ssid = "osBalakinhas";
char* password = "balakubaku";
int LED = 2;
WiFiServer server(80);

void comunicacaoInit() {
  Serial.begin(9600);
  pinMode(LED, OUTPUT);

  Serial.println();
  Serial.print("Conectando-se a ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi conectada.");
  Serial.println("Endereço de IP: ");
  Serial.println(WiFi.localIP());

  server.begin();
}

String buildStatusJson(const String& sensor, const JSONVar& fields) {
  JSONVar obj;
  obj["device"] = "esp32";
  obj["sensor"] = sensor;
  obj["data"] = fields;
  obj["ts"] = (double)millis(); 
  return JSON.stringify(obj);
}

String buildStatusJson(const String& sensor, const char* keys[], const double values[], size_t count) {
  JSONVar data;
  for (size_t i = 0; i < count; ++i) {
    if (keys[i]) data[keys[i]] = values[i];
  }
  return buildStatusJson(sensor, data);
}

// Função que envia a resposta HTTP com JSON
void sendJson(WiFiClient& client, const String& json) {
  client.println("HTTP/1.1 200 OK");
  client.println("Content-Type: application/json");
  client.print("Content-Length: ");
  client.println(json.length());
  client.println("Connection: close");
  client.println();
  client.print(json);
}

// Processamento por requisição (antes era loop)
void comunicacaoProcess() {
  WiFiClient client = server.available();
  if (!client) return;
  Serial.println("New Client.");
  String currentLine = "";
  bool requestedStatus = false;
  while (client.connected()) {
    if (client.available()) {
      char c = client.read();
      Serial.write(c);
      if (c == '\n') {
        if (currentLine.length() == 0) {
          if (requestedStatus) {
            double rpm = (millis() / 100) % 4000;
            double temp = 20.0 + ((millis() / 1000) % 15);
            const char* keys[] = {"rpm", "temp"};
            double vals[] = {rpm, temp};
            String payload = buildStatusJson("motor", keys, vals, 2);
            sendJson(client, payload);
          } else {
            client.println("HTTP/1.1 200 OK");
            client.println("Content-type:text/html");
            client.println();
            client.print("Click <a href=\"/H\">here</a> to turn the LED on pin 2 on.<br>");
            client.print("Click <a href=\"/L\">here</a> to turn the LED on pin 2 off.<br>");
            client.print("Get <a href=\"/status\">status</a> as JSON.<br>");
            client.println();
          }
          break;
        } else {
          currentLine = "";
        }
      } else if (c != '\r') {
        currentLine += c;
      }
      if (currentLine.endsWith("GET /H")) digitalWrite(LED, HIGH);
      if (currentLine.endsWith("GET /L")) digitalWrite(LED, LOW);
      if (currentLine.endsWith("GET /status")) requestedStatus = true;
    }
  }
  client.stop();
  Serial.println("Client Disconnected.");
}