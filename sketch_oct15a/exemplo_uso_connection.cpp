// /*
//  * ⚠️ ARQUIVO DE REFERÊNCIA - NÃO COMPILAR DIRETAMENTE
//  * 
//  * Este arquivo contém exemplos de uso da classe Connection.
//  * NÃO inclua este arquivo no projeto Arduino (foi renomeado para .cpp).
//  * 
//  * Para usar os exemplos:
//  * 1. Copie o código desejado
//  * 2. Cole no arquivo sketch_oct15a.ino
//  * 3. Adapte conforme necessário
//  * 
//  * A classe Connection já está disponível via comunicacao.ino
//  */

// /*
//  * Exemplo de uso da classe Connection
//  * 
//  * Este arquivo demonstra como usar a nova classe Connection
//  * para enviar dados de sensores via MQTT e HTTP
//  */

// // A classe Connection já está definida em comunicacao.ino
// // Certifique-se de incluir este arquivo no seu projeto

// void setup() {
//   // Inicializa a conexão WiFi, MQTT e HTTP Server
//   comunicacaoInit();
  
//   // Aguarda até WiFi conectar
//   while (!connection.isWiFiConnected()) {
//     Serial.println("Aguardando WiFi...");
//     delay(1000);
//   }
  
//   Serial.println("=================================");
//   Serial.println("Sistema iniciado com sucesso!");
//   Serial.println("Device ID: " + connection.getDeviceId());
//   Serial.println("IP Local: " + connection.getDeviceIP());
//   Serial.println("MQTT: " + String(connection.isMQTTConnected() ? "Conectado" : "Desconectado"));
//   Serial.println("=================================");
// }

// void loop() {
//   // IMPORTANTE: Chama tick() para manter conexões ativas
//   comunicacaoTick();
  
//   // ========================================================================
//   // EXEMPLO 1: Enviar dados usando JSONVar
//   // ========================================================================
//   static unsigned long lastSend1 = 0;
//   if (millis() - lastSend1 > 10000) {  // A cada 10 segundos
//     JSONVar dadosMotor;
//     dadosMotor["rpm"] = random(1000, 4000);
//     dadosMotor["temp"] = random(20, 45);
//     dadosMotor["voltage"] = 12.0 + random(-50, 50) / 100.0;
//     dadosMotor["current"] = 2.5 + random(-30, 30) / 100.0;
    
//     if (enviarDadosSensor("motor", dadosMotor)) {
//       Serial.println("✓ Dados do motor enviados!");
//     }
    
//     lastSend1 = millis();
//   }
  
//   // ========================================================================
//   // EXEMPLO 2: Enviar dados usando arrays (mais eficiente para poucos campos)
//   // ========================================================================
//   static unsigned long lastSend2 = 0;
//   if (millis() - lastSend2 > 15000) {  // A cada 15 segundos
//     const char* campos[] = {"temperatura", "umidade"};
//     double valores[] = {23.5, 65.2};
    
//     if (enviarDadosSensor("DHT11", campos, valores, 2)) {
//       Serial.println("✓ Dados de temperatura enviados!");
//     }
    
//     lastSend2 = millis();
//   }
  
//   // ========================================================================
//   // EXEMPLO 3: Enviar dados via HTTP POST para servidor externo
//   // ========================================================================
//   static unsigned long lastSend3 = 0;
//   if (millis() - lastSend3 > 30000) {  // A cada 30 segundos
//     JSONVar payload;
//     payload["device"] = connection.getDeviceId();
//     payload["sensor"] = "status";
//     payload["wifi_rssi"] = WiFi.RSSI();
//     payload["uptime"] = millis();
    
//     // Envia para servidor HTTP externo (exemplo)
//     // Altere o IP e porta para seu servidor
//     if (enviarHTTPPost("192.168.1.100", 5000, "/api/status", payload)) {
//       Serial.println("✓ Status enviado via HTTP!");
//     }
    
//     lastSend3 = millis();
//   }
  
//   // ========================================================================
//   // EXEMPLO 4: Usando diretamente o objeto connection
//   // ========================================================================
//   static unsigned long lastSend4 = 0;
//   if (millis() - lastSend4 > 20000) {  // A cada 20 segundos
//     // Dados de um encoder
//     JSONVar dadosEncoder;
//     dadosEncoder["posicao"] = random(0, 360);
//     dadosEncoder["velocidade"] = random(0, 100);
//     dadosEncoder["direcao"] = random(0, 2) == 0 ? "horario" : "antihorario";
    
//     connection.sendSensorData("Encoder", dadosEncoder);
    
//     lastSend4 = millis();
//   }
  
//   // ========================================================================
//   // EXEMPLO 5: Verificar status da conexão
//   // ========================================================================
//   static unsigned long lastCheck = 0;
//   if (millis() - lastCheck > 60000) {  // A cada 60 segundos
//     Serial.println("\n=== STATUS DA CONEXÃO ===");
//     Serial.println("WiFi: " + String(connection.isWiFiConnected() ? "✓ Conectado" : "✗ Desconectado"));
//     Serial.println("MQTT: " + String(connection.isMQTTConnected() ? "✓ Conectado" : "✗ Desconectado"));
//     Serial.println("IP: " + connection.getDeviceIP());
//     Serial.println("Uptime: " + String(millis() / 1000) + " segundos");
//     Serial.println("========================\n");
    
//     lastCheck = millis();
//   }
  
//   // Pequeno delay para não sobrecarregar o loop
//   delay(10);
// }

// // ========================================================================
// // FUNÇÕES AUXILIARES - Exemplo de como criar wrappers para sensores
// // ========================================================================

// // Envia dados de um sensor de temperatura e umidade
// void enviarDadosAmbiente(float temperatura, float umidade, float pressao = 0) {
//   JSONVar dados;
//   dados["temperatura"] = temperatura;
//   dados["umidade"] = umidade;
//   if (pressao > 0) {
//     dados["pressao"] = pressao;
//   }
  
//   connection.sendSensorData("DHT11", dados);
// }

// // Envia dados de tentativa de acesso via teclado
// void enviarTentativaAcesso(bool autorizado, int numTentativas, int senhaLength) {
//   JSONVar dados;
//   dados["authorized"] = autorizado ? 1 : 0;
//   dados["attempts"] = numTentativas;
//   dados["password_length"] = senhaLength;
//   dados["vibration_duration"] = autorizado ? 200 : 600;
  
//   connection.sendSensorData("Teclado 4x4", dados);
// }

// // Envia estado da porta (relé + encoder)
// void enviarEstadoPorta(bool travada, int anguloAbertura) {
//   JSONVar dados;
//   dados["relay"] = travada ? 1 : 0;
//   dados["door_angle"] = anguloAbertura;
//   dados["door_open"] = anguloAbertura > 10 ? 1 : 0;
//   dados["lock_cycles"] = random(0, 100);
  
//   connection.sendSensorData("Relé JQC3F", dados);
// }

// // Envia estado dos LEDs de status
// void enviarEstadoLEDs(int ledVerde, int ledAmarelo, int ledVermelho) {
//   JSONVar dados;
//   dados["led_green"] = ledVerde;
//   dados["led_yellow"] = ledAmarelo;
//   dados["led_red"] = ledVermelho;
//   dados["brightness"] = 255;
  
//   connection.sendSensorData("KY023", dados);
// }
