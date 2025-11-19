#include "comunicacao.h"

// ============================================================================
// Callback para processar comandos recebidos do servidor
// ============================================================================
void processarComando(const String& command, const JSONVar& params) {
  Serial.println("\n========================================");
  Serial.println("COMANDO RECEBIDO DO SERVIDOR:");
  Serial.println("Comando: " + command);
  Serial.println("Parâmetros: " + JSON.stringify(params));
  Serial.println("========================================");
  
  // Processa comando "retorno"
  if (command == "retorno") {
    if (params.hasOwnProperty("retorno")) {
      bool retornoValue = (bool)params["retorno"];
      
      if (retornoValue == true) {
        Serial.println("✓✓✓ RETORNO = TRUE recebido do servidor! ✓✓✓");
        Serial.println("Operação confirmada com sucesso!");
        
        // Exemplo: piscar LED 3 vezes
        for (int i = 0; i < 3; i++) {
          digitalWrite(2, HIGH);
          delay(200);
          digitalWrite(2, LOW);
          delay(200);
        }
      } else {
        Serial.println("✗✗✗ RETORNO = FALSE recebido do servidor! ✗✗✗");
        Serial.println("Operação não foi bem-sucedida.");
      }
    }
  }
  
  // Processa outros comandos personalizados
  else if (command == "status") {
    Serial.println("Comando STATUS recebido");
    if (params.hasOwnProperty("message")) {
      String msg = (const char*)params["message"];
      Serial.println("Mensagem: " + msg);
    }
  }
  
  else if (command == "config") {
    Serial.println("Comando CONFIG recebido");
    if (params.hasOwnProperty("interval")) {
      int interval = (int)params["interval"];
      Serial.println("Novo intervalo: " + String(interval) + " ms");
    }
  }
  
  else {
    Serial.println("⚠ Comando desconhecido: " + command);
  }
  
  Serial.println("========================================\n");
}

void setup() {
  Serial.begin(9600);
  pinMode(2, OUTPUT);  // LED interno
  
  // Inicializa comunicação com nome personalizado
  comunicacaoInit("ESP32_LAB_002");
  
  // Registra o callback para processar comandos do servidor
  comunicacaoSetCallback(processarComando);
  
  Serial.println("\n✓ Sistema iniciado!");
  Serial.println("✓ Callback registrado para receber comandos do servidor");
  Serial.println("Aguardando comandos via MQTT ou HTTP...\n");
}

void loop() {
  comunicacaoTick();  // Mantém conexões ativas
  
  
  
}