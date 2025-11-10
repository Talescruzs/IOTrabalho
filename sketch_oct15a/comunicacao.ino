#include <WiFi.h>
#include <Arduino_JSON.h>
#include <HTTPClient.h>
char* ssid = "osBalakinhas";
char* password = "balakubaku";
int LED = 2;
WiFiServer server(80);
const char* API_URL = "http://192.168.143.117:5000/esp/ingest"; // ajuste para o IP/host da API
const char* API_HOST = "192.168.143.117"; // separado para teste de ping

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

void pushStatusPeriodic() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi desconectado, abortando push");
    return;
  }
  static unsigned long lastPush = 0;
  if (millis() - lastPush < 5000) return;

  Serial.printf("Preparando POST para %s...\n", API_URL);

  double rpm = (millis() / 100) % 4000;
  double temp = 20.0 + ((millis() / 1000) % 15);
  const char* keys[] = {"rpm", "temp"};
  double vals[] = {rpm, temp};
  String payload = buildStatusJson("motor", keys, vals, 2);
  
  Serial.print("Payload: ");
  Serial.println(payload);

  WiFiClient net;
  HTTPClient http;
  http.setTimeout(5000);
  
  Serial.println("Iniciando conexão HTTP...");
  if (!http.begin(net, API_URL)) {
    Serial.println("ERRO: HTTP begin falhou");
    lastPush = millis();
    return;
  }
  
  http.addHeader("Content-Type", "application/json");
  http.addHeader("Connection", "close");

  Serial.println("Enviando POST...");
  int code = http.POST(payload);
  
  if (code > 0) {
    String resp = http.getString();
    Serial.printf("✓ Push OK - status: %d, resp: %s\n", code, resp.c_str());
  } else {
    Serial.printf("✗ Push FALHOU - código: %d, erro: %s\n", code, http.errorToString(code).c_str());
    Serial.println("Verificações:");
    Serial.printf("  1. API rodando? curl http://192.168.143.117:5000/esp/latest\n");
    Serial.printf("  2. Firewall liberado na porta 5000?\n");
    Serial.printf("  3. Mesma rede WiFi? ESP: %s\n", WiFi.localIP().toString().c_str());
  }
  http.end();
  lastPush = millis();
}

// Tick chamado no loop principal
void comunicacaoTick() {
  pushStatusPeriodic();
  comunicacaoProcess();
}