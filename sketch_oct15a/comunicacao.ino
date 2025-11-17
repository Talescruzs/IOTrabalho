// // ============================================================================#include <WiFi.h>

// // WRAPPER PARA COMPATIBILIDADE COM Connection.h#include <Arduino_JSON.h>

// // ============================================================================#include <PubSubClient.h>

// #include "Connection.h"

// // ============================================================================

// // ============================================================================// Classe Connection - Gerencia comunicação WiFi, MQTT e HTTP

// // CONFIGURAÇÕES (Modifique aqui)// ============================================================================

// // ============================================================================class Connection {

// char* ssid = "osBalakinhas";private:

// char* password = "balakubaku";  // Configurações WiFi

// const char* MQTT_BROKER = "192.168.143.117";  const char* _ssid;

// const char* DEVICE_ID = "esp32";  const char* _password;

// const uint16_t MQTT_PORT = 1883;  int _ledPin;

// const int LED_PIN = 2;  

// const uint16_t HTTP_PORT = 80;  // Configurações MQTT

//   const char* _mqttBroker;

// // ============================================================================  uint16_t _mqttPort;

// // Instância global da conexão  const char* _deviceId;

// // ============================================================================  String _deviceIP;

// Connection connection(ssid, password, DEVICE_ID, MQTT_BROKER, MQTT_PORT, LED_PIN, HTTP_PORT);  

//   // Clientes

// // ============================================================================  WiFiClient _espClient;

// // Funções de interface (compatibilidade com código antigo)  PubSubClient _mqttClient;

// // ============================================================================  WiFiServer _httpServer;

  

// void comunicacaoInit() {  // Estado da conexão

//   connection.begin();  bool _wifiConnected;

// }  bool _mqttConnected;

//   unsigned long _lastMqttReconnect;

// void comunicacaoProcess() {  unsigned long _lastSensorSend;

//   connection.processHTTP();  

// }  // Callback MQTT estática (necessário para PubSubClient)

//   static Connection* _instance;

// void comunicacaoTick() {  static void staticMqttCallback(char* topic, byte* payload, unsigned int length) {

//   connection.tick();    if (_instance) {

// }      _instance->onMqttMessage(topic, payload, length);

//     }

// // ============================================================================  }

// // Funções auxiliares para envio de dados  

// // ============================================================================  // Callback MQTT de instância

//   void onMqttMessage(char* topic, byte* payload, unsigned int length) {

// // Envia dados de sensor via MQTT usando JSONVar    Serial.print("\n>>> Mensagem MQTT recebida [");

// bool enviarDadosSensor(const String& sensorName, const JSONVar& data) {    Serial.print(topic);

//   return connection.sendSensorData(sensorName, data);    Serial.print("]: ");

// }    

//     String message = "";

// // Envia dados de sensor via MQTT usando arrays    for (unsigned int i = 0; i < length; i++) {

// bool enviarDadosSensor(const String& sensorName, const char* keys[], const double values[], size_t count) {      message += (char)payload[i];

//   return connection.sendSensorData(sensorName, keys, values, count);    }

// }    Serial.println(message);

    

// // Envia dados para servidor externo via HTTP POST    // Pisca LED quando recebe confirmação

// bool enviarHTTPPost(const char* serverHost, uint16_t serverPort, const String& endpoint, const JSONVar& data) {    digitalWrite(_ledPin, HIGH);

//   String jsonPayload = JSON.stringify(data);    delay(200);

//   return connection.sendHTTPPost(serverHost, serverPort, endpoint, jsonPayload);    digitalWrite(_ledPin, LOW);

// }  }

  
//   // Conecta ao WiFi
//   bool connectWiFi() {
//     Serial.println();
//     Serial.print("Conectando-se a ");
//     Serial.println(_ssid);
//     WiFi.begin(_ssid, _password);

//     unsigned long start = millis();
//     while (WiFi.status() != WL_CONNECTED && millis() - start < 10000) {
//       delay(500);
//       Serial.print(".");
//     }

//     if (WiFi.status() == WL_CONNECTED) {
//       _wifiConnected = true;
//       _deviceIP = WiFi.localIP().toString();
//       Serial.println("");
//       Serial.println("WiFi conectada.");
//       Serial.print("Endereço IP: ");
//       Serial.println(_deviceIP);
//       return true;
//     } else {
//       _wifiConnected = false;
//       Serial.println("\nFalha ao conectar WiFi!");
//       return false;
//     }
//   }
  
//   // Conecta ao broker MQTT
//   bool connectMQTT() {
//     if (!_wifiConnected) {
//       Serial.println("WiFi não conectado. Impossível conectar MQTT.");
//       return false;
//     }
    
//     _mqttClient.setServer(_mqttBroker, _mqttPort);
//     _mqttClient.setCallback(staticMqttCallback);
    
//     unsigned long start = millis();
//     while (!_mqttClient.connected() && millis() - start < 5000) {
//       Serial.println("Conectando ao broker MQTT...");
      
//       if (_mqttClient.connect(_deviceId)) {
//         _mqttConnected = true;
//         Serial.println("✓ Conectado ao MQTT broker.");
        
//         // Subscreve em tópicos de resposta
//         String confirmTopic = "iot/confirm/" + String(_deviceId);
//         String responseTopic = "iot/response/" + String(_deviceId);
        
//         _mqttClient.subscribe(confirmTopic.c_str());
//         _mqttClient.subscribe(responseTopic.c_str());
        
//         Serial.println("✓ Subscrito em: " + confirmTopic + " e " + responseTopic);
        
//         // Registra dispositivo
//         registerDevice();
        
//         return true;
//       } else {
//         Serial.print("✗ Falha MQTT, rc=");
//         Serial.print(_mqttClient.state());
//         Serial.println(" - tentando novamente...");
//         delay(1000);
//       }
//     }
    
//     _mqttConnected = false;
//     return false;
//   }
  
//   // Registra dispositivo no servidor
//   void registerDevice() {
//     if (!_mqttConnected) return;
    
//     JSONVar registerData;
//     registerData["device_id"] = _deviceId;
//     registerData["ip"] = _deviceIP;
    
//     String registerMsg = JSON.stringify(registerData);
    
//     if (_mqttClient.publish("iot/register", registerMsg.c_str())) {
//       Serial.println("✓ Dispositivo registrado: " + registerMsg);
      
//       // Aguarda confirmação
//       unsigned long waitStart = millis();
//       while (millis() - waitStart < 3000) {
//         _mqttClient.loop();
//         delay(10);
//       }
//     } else {
//       Serial.println("✗ Falha ao registrar dispositivo");
//     }
//   }

// public:
//   // Construtor
//   Connection(const char* ssid, const char* password, const char* deviceId, 
//              const char* mqttBroker, uint16_t mqttPort = 1883, int ledPin = 2, uint16_t httpPort = 80)
//     : _ssid(ssid), 
//       _password(password), 
//       _deviceId(deviceId),
//       _mqttBroker(mqttBroker), 
//       _mqttPort(mqttPort),
//       _ledPin(ledPin),
//       _mqttClient(_espClient),
//       _httpServer(httpPort),
//       _wifiConnected(false),
//       _mqttConnected(false),
//       _lastMqttReconnect(0),
//       _lastSensorSend(0) {
//     _instance = this;
//   }
  
//   // Inicializa todas as conexões
//   bool begin() {
//     Serial.begin(9600);
//     pinMode(_ledPin, OUTPUT);
    
//     // Conecta WiFi
//     if (!connectWiFi()) {
//       return false;
//     }
    
//     // Inicia servidor HTTP
//     _httpServer.begin();
//     Serial.println("✓ Servidor HTTP iniciado");
    
//     // Conecta MQTT
//     connectMQTT();
    
//     return _wifiConnected;
//   }
  
//   // Envia dados de sensor via MQTT
//   bool sendSensorData(const String& sensorName, const JSONVar& data) {
//     if (!_mqttConnected) {
//       Serial.println("✗ MQTT não conectado. Impossível enviar dados.");
//       return false;
//     }
    
//     JSONVar message;
//     message["device_id"] = _deviceId;
//     message["sensor"] = sensorName;
//     message["data"] = data;
//     message["timestamp"] = String(millis());
    
//     String payload = JSON.stringify(message);
//     String topic = "iot/sensor/" + String(_deviceId);
    
//     if (_mqttClient.publish(topic.c_str(), payload.c_str())) {
//       Serial.println("✓ Dados enviados [" + sensorName + "]: " + payload);
//       return true;
//     } else {
//       Serial.println("✗ Falha ao enviar dados de " + sensorName);
//       return false;
//     }
//   }
  
//   // Envia dados de sensor via MQTT (versão com arrays)
//   bool sendSensorData(const String& sensorName, const char* keys[], const double values[], size_t count) {
//     JSONVar data;
//     for (size_t i = 0; i < count; i++) {
//       if (keys[i]) {
//         data[keys[i]] = values[i];
//       }
//     }
//     return sendSensorData(sensorName, data);
//   }
  
//   // Envia dados via HTTP POST para servidor externo
//   bool sendHTTPPost(const char* serverHost, uint16_t serverPort, const String& endpoint, const String& jsonPayload) {
//     if (!_wifiConnected) {
//       Serial.println("✗ WiFi não conectado. Impossível enviar HTTP POST.");
//       return false;
//     }
    
//     WiFiClient client;
//     if (!client.connect(serverHost, serverPort)) {
//       Serial.println("✗ Falha ao conectar ao servidor HTTP " + String(serverHost) + ":" + String(serverPort));
//       return false;
//     }
    
//     // Constrói requisição HTTP POST
//     client.println("POST " + endpoint + " HTTP/1.1");
//     client.println("Host: " + String(serverHost));
//     client.println("Content-Type: application/json");
//     client.print("Content-Length: ");
//     client.println(jsonPayload.length());
//     client.println("Connection: close");
//     client.println();
//     client.print(jsonPayload);
    
//     // Aguarda resposta
//     unsigned long timeout = millis();
//     while (client.available() == 0) {
//       if (millis() - timeout > 5000) {
//         Serial.println("✗ Timeout na resposta HTTP");
//         client.stop();
//         return false;
//       }
//     }
    
//     // Lê resposta
//     while (client.available()) {
//       String line = client.readStringUntil('\r');
//       Serial.print(line);
//     }
    
//     client.stop();
//     Serial.println("\n✓ HTTP POST enviado com sucesso");
//     return true;
//   }
  
//   // Processa requisições HTTP do servidor local
//   void processHTTP() {
//     WiFiClient client = _httpServer.available();
//     if (!client) return;
    
//     Serial.println("Novo cliente HTTP.");
//     String currentLine = "";
//     bool requestedStatus = false;
    
//     while (client.connected()) {
//       if (client.available()) {
//         char c = client.read();
//         Serial.write(c);
        
//         if (c == '\n') {
//           if (currentLine.length() == 0) {
//             if (requestedStatus) {
//               // Responde com status em JSON
//               double rpm = (millis() / 100) % 4000;
//               double temp = 20.0 + ((millis() / 1000) % 15);
//               const char* keys[] = {"rpm", "temp"};
//               double vals[] = {rpm, temp};
              
//               JSONVar data;
//               for (int i = 0; i < 2; i++) {
//                 data[keys[i]] = vals[i];
//               }
              
//               JSONVar statusObj;
//               statusObj["device"] = _deviceId;
//               statusObj["sensor"] = "motor";
//               statusObj["data"] = data;
//               statusObj["ts"] = (double)millis();
              
//               String json = JSON.stringify(statusObj);
//               sendJsonResponse(client, json);
//             } else {
//               // Responde com HTML
//               client.println("HTTP/1.1 200 OK");
//               client.println("Content-type:text/html");
//               client.println();
//               client.print("Click <a href=\"/H\">here</a> to turn LED ON.<br>");
//               client.print("Click <a href=\"/L\">here</a> to turn LED OFF.<br>");
//               client.print("Get <a href=\"/status\">status</a> as JSON.<br>");
//               client.println();
//             }
//             break;
//           } else {
//             currentLine = "";
//           }
//         } else if (c != '\r') {
//           currentLine += c;
//         }
        
//         // Processa comandos
//         if (currentLine.endsWith("GET /H")) digitalWrite(_ledPin, HIGH);
//         if (currentLine.endsWith("GET /L")) digitalWrite(_ledPin, LOW);
//         if (currentLine.endsWith("GET /status")) requestedStatus = true;
//       }
//     }
    
//     client.stop();
//     Serial.println("Cliente HTTP desconectado.");
//   }
  
//   // Envia resposta JSON via HTTP
//   void sendJsonResponse(WiFiClient& client, const String& json) {
//     client.println("HTTP/1.1 200 OK");
//     client.println("Content-Type: application/json");
//     client.print("Content-Length: ");
//     client.println(json.length());
//     client.println("Connection: close");
//     client.println();
//     client.print(json);
//   }
  
//   // Loop de manutenção (deve ser chamado no loop principal)
//   void tick() {
//     // Mantém MQTT ativo
//     if (_mqttConnected && _mqttClient.connected()) {
//       _mqttClient.loop();
//     } else if (_wifiConnected) {
//       // Tenta reconectar MQTT se perdeu conexão
//       if (millis() - _lastMqttReconnect > 5000) {
//         Serial.println("MQTT desconectado. Tentando reconectar...");
//         connectMQTT();
//         _lastMqttReconnect = millis();
//       }
//     }
    
//     // Processa requisições HTTP
//     processHTTP();
//   }
  
//   // Getters
//   bool isWiFiConnected() const { return _wifiConnected; }
//   bool isMQTTConnected() const { return _mqttConnected; }
//   String getDeviceIP() const { return _deviceIP; }
//   String getDeviceId() const { return String(_deviceId); }
// };

// // Inicializa ponteiro estático
// Connection* Connection::_instance = nullptr;

// // Configurações
// char* ssid = "osBalakinhas";
// char* password = "balakubaku";
// const char* MQTT_BROKER = "192.168.143.117";
// const char* DEVICE_ID = "esp32";

// // Instância global da conexão
// Connection connection(ssid, password, DEVICE_ID, MQTT_BROKER);

// // ============================================================================
// // Funções de interface (compatibilidade com código antigo)
// // ============================================================================

// void comunicacaoInit() {
//   connection.begin();
// }

// void comunicacaoProcess() {
//   connection.processHTTP();
// }

// void comunicacaoTick() {
//   connection.tick();
// }

// // ============================================================================
// // Funções auxiliares para envio de dados
// // ============================================================================

// // Envia dados de sensor via MQTT usando JSONVar
// bool enviarDadosSensor(const String& sensorName, const JSONVar& data) {
//   return connection.sendSensorData(sensorName, data);
// }

// // Envia dados de sensor via MQTT usando arrays
// bool enviarDadosSensor(const String& sensorName, const char* keys[], const double values[], size_t count) {
//   return connection.sendSensorData(sensorName, keys, values, count);
// }

// // Envia dados para servidor externo via HTTP POST
// bool enviarHTTPPost(const char* serverHost, uint16_t serverPort, const String& endpoint, const JSONVar& data) {
//   String jsonPayload = JSON.stringify(data);
//   return connection.sendHTTPPost(serverHost, serverPort, endpoint, jsonPayload);
// }