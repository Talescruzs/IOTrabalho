// ============================================================================
// comunicacao.h - Interface de compatibilidade para Connection
// ============================================================================
#ifndef COMUNICACAO_H
#define COMUNICACAO_H

#include <Arduino_JSON.h>

// ============================================================================
// Tipo de callback para processar comandos recebidos do servidor
// ============================================================================
typedef void (*CommandCallback)(const String& command, const JSONVar& params);

// ============================================================================
// Funções de inicialização e manutenção
// ============================================================================

// Inicializa WiFi, MQTT e HTTP
void comunicacaoInit(String nome_esp);

// Registra callback para processar comandos do servidor
void comunicacaoSetCallback(CommandCallback callback);

// Processa requisições HTTP
void comunicacaoProcess();

// Mantém conexões ativas (chame no loop)
void comunicacaoTick();

// ============================================================================
// Funções de envio de dados
// ============================================================================

// Envia dados de sensor via MQTT usando JSONVar
bool enviarDadosSensor(const String& sensorName, const JSONVar& data);

// Envia dados de sensor via MQTT usando arrays
bool enviarDadosSensor(const String& sensorName, const char* keys[], const double values[], size_t count);

// Envia dados para servidor externo via HTTP POST
bool enviarHTTPPost(const char* serverHost, uint16_t serverPort, const String& endpoint, const JSONVar& data);

#endif // COMUNICACAO_H
