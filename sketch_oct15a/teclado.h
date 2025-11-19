// ============================================================================
// teclado.h - Interface para Teclado Matricial 4x4
// ============================================================================
#ifndef TECLADO_H
#define TECLADO_H

#include <Arduino.h>
#include <Keypad.h>

// ============================================================================
// Constantes do teclado
// ============================================================================
extern const byte LINHAS;
extern const byte COLUNAS;
extern const char TECLAS_MATRIZ[4][4];
extern byte PINOS_LINHAS[4];
extern byte PINOS_COLUNAS[4];

// ============================================================================
// Objeto global do teclado
// ============================================================================
extern Keypad teclado_personalizado;

// ============================================================================
// Funções de interface
// ============================================================================

// Inicializa o teclado (chame no setup)
void tecladoInit();

// Lê tecla pressionada (retorna 0 se nenhuma tecla foi pressionada)
char tecladoLerTecla();

// Aguarda até que uma tecla seja pressionada e retorna
char tecladoAguardarTecla();

// Verifica se alguma tecla está pressionada
bool tecladoTeclaPressionada();

#endif // TECLADO_H