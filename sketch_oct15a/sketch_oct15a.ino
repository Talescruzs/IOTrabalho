#include "comunicacao.h"
#include "teclado.h"

// Variáveis para gerenciar entrada do teclado
String senhaDigitada = "";
const int MAX_SENHA = 10;
unsigned long ultimaTecla = 0;
const unsigned long TIMEOUT_SENHA = 5000; // 5 segundos de timeout

void setup() {
  comunicacaoInit();  // Conecta WiFi e MQTT
  tecladoInit();      // Inicializa teclado
  
  Serial.println("\n=== Sistema de Acesso com Teclado ===");
  Serial.println("Digite uma senha e pressione # para enviar");
  Serial.println("Pressione * para limpar\n");
}

void loop() {
  comunicacaoTick();  // Mantém conexões ativas
  
  // Lê tecla do teclado matricial
  char tecla = tecladoLerTecla();
  
  if (tecla) {
    Serial.print("Tecla pressionada: ");
    Serial.println(tecla);
    
    // Atualiza timestamp da última tecla
    ultimaTecla = millis();
    
    if (tecla == '#') {
      // Envia a senha digitada para o servidor
      if (senhaDigitada.length() > 0) {
        enviarDadosTeclado();
        senhaDigitada = ""; // Limpa senha após enviar
        Serial.println("Senha enviada! Digite nova senha...\n");
      } else {
        Serial.println("Senha vazia! Digite algo antes de #\n");
      }
    } 
    else if (tecla == '*') {
      // Limpa a senha digitada
      senhaDigitada = "";
      Serial.println("Senha limpa!\n");
    }
    else {
      // Adiciona tecla à senha (se não exceder limite)
      if (senhaDigitada.length() < MAX_SENHA) {
        senhaDigitada += tecla;
        Serial.print("Senha atual: ");
        for (int i = 0; i < senhaDigitada.length(); i++) {
          Serial.print("*"); // Mostra asteriscos por segurança
        }
        Serial.print(" (");
        Serial.print(senhaDigitada.length());
        Serial.println(" dígitos)");
      } else {
        Serial.println("Limite de caracteres atingido! Pressione # para enviar ou * para limpar");
      }
    }
  }
  
  // Timeout: limpa senha se ficar muito tempo sem digitar
  if (senhaDigitada.length() > 0 && (millis() - ultimaTecla > TIMEOUT_SENHA)) {
    Serial.println("\nTimeout! Senha limpa automaticamente.");
    senhaDigitada = "";
  }
  
  // Envio periódico de dados de sensores (mantido)
  static unsigned long lastSend = 0;
  if (millis() - lastSend > 30000) {  // A cada 30 segundos
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

// Função para enviar dados do teclado
void enviarDadosTeclado() {
  JSONVar dados;
  dados["password"] = senhaDigitada.c_str();
  dados["length"] = (int)senhaDigitada.length();
  dados["timestamp_entrada"] = (double)ultimaTecla;
  
  // Simula validação local (em produção, seria no servidor)
  bool autorizado = (senhaDigitada == "1234"); // Senha correta: 1234
  dados["authorized"] = autorizado ? 1 : 0;
  
  Serial.println("\n--- Enviando dados do teclado ---");
  Serial.print("Senha: ");
  Serial.println(senhaDigitada);
  Serial.print("Autorizado: ");
  Serial.println(autorizado ? "SIM" : "NÃO");
  
  enviarDadosSensor("teclado", dados);
  
  Serial.println("--- Dados enviados ---\n");
}