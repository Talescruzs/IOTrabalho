#include <WiFi.h>
#include <Arduino_JSON.h>
#include <PubSubClient.h>

char* ssid = "osBalakinhas";
char* password = "balakubaku";
int LED = 2;
WiFiServer server(80);

// MQTT config
const char* MQTT_BROKER = "192.168.143.117"; // altere para seu broker
const uint16_t MQTT_PORT = 1883;
const char* MQTT_TOPIC = "iot/register";  // tópico mudou para registro

WiFiClient espClient;
PubSubClient mqttClient(espClient);

// Callback quando recebe mensagem MQTT
void onMqttMessage(char* topic, byte* payload, unsigned int length) {
  Serial.print("\n>>> Mensagem MQTT recebida [");
  Serial.print(topic);
  Serial.print("]: ");
  
  String message = "";
  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println(message);
  
  // Pisca LED quando recebe confirmação
  digitalWrite(LED, HIGH);
  delay(200);
  digitalWrite(LED, LOW);
}

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

  // MQTT init - registra IP uma vez
  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  mqttClient.setCallback(onMqttMessage);  // registra callback

  unsigned long start = millis();
  while (!mqttClient.connected() && millis() - start < 5000) {
    Serial.println("Conectando ao broker MQTT para registro...");
    if (mqttClient.connect("esp32-client")) {
      Serial.println("Conectado ao MQTT broker.");

      // Subscreve no tópico de confirmação E resposta
      mqttClient.subscribe("iot/confirm/esp32");
      mqttClient.subscribe("iot/response/esp32");
      Serial.println("Subscrito em: iot/confirm/esp32 e iot/response/esp32");

      // Envia mensagem de registro com IP
      String registerMsg = "{\"device_id\":\"esp32\",\"ip\":\"" + WiFi.localIP().toString() + "\"}";
      mqttClient.publish(MQTT_TOPIC, registerMsg.c_str());
      Serial.println("IP registrado via MQTT: " + registerMsg);

      // Aguarda confirmação por 3 segundos
      unsigned long waitStart = millis();
      while (millis() - waitStart < 3000) {
        mqttClient.loop();
        delay(10);
      }

      Serial.println("Mantendo conexão MQTT ativa para receber comandos...");
      // NÃO desconecta - mantém conectado para receber respostas
      break;
    } else {
      Serial.print("Falha MQTT, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" tentando novamente...");
      delay(1000);
    }
  }
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

// Função que envia a resposta HTTP com JSON (servidor local)
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

// Tick chamado no loop principal
void comunicacaoTick() {
  // Mantém MQTT ativo para receber respostas
  if (mqttClient.connected()) {
    mqttClient.loop();
  } else {
    // Tenta reconectar se perdeu conexão
    static unsigned long lastReconnect = 0;
    if (millis() - lastReconnect > 5000) {
      Serial.println("MQTT desconectado, tentando reconectar...");
      if (mqttClient.connect("esp32-client")) {
        Serial.println("MQTT reconectado!");
        mqttClient.subscribe("iot/confirm/esp32");
        mqttClient.subscribe("iot/response/esp32");
      }
      lastReconnect = millis();
    }
  }
  
  // Envia dados de sensor periodicamente
  static unsigned long lastSensorSend = 0;
  if (millis() - lastSensorSend > 10000) {  // a cada 10 segundos
    if (mqttClient.connected()) {
      double rpm = (millis() / 100) % 4000;
      double temp = 20.0 + ((millis() / 1000) % 15);
      
      String sensorMsg = "{\"device_id\":\"esp32\",\"sensor\":\"motor\",\"data\":{\"rpm\":" + 
                        String(rpm) + ",\"temp\":" + String(temp) + "}}";
      
      mqttClient.publish("iot/sensor/esp32", sensorMsg.c_str());
      Serial.println("Dados de sensor enviados: " + sensorMsg);
    }
    lastSensorSend = millis();
  }
  
  comunicacaoProcess();
}