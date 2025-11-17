/*******************************************************************************
* Teclado Matricial 16 Teclas : Primeiros Passos (v1.0)
*
* Codigo base para exibir as teclas pressionadas no monitor serial da IDE.
*
* Copyright 2020 RoboCore.
* Escrito por Matheus Cassioli (30/07/2019).
* Atualizado por Giovanni de Castro (22/01/2020).
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version (<https://www.gnu.org/licenses/>).
******************************************************************************/

#include "teclado.h"

// ============================================================================
// Configuração do teclado
// ============================================================================
const byte LINHAS = 4; // Linhas do teclado
const byte COLUNAS = 4; // Colunas do teclado

const char TECLAS_MATRIZ[LINHAS][COLUNAS] = { // Matriz de caracteres (mapeamento do teclado)
  {'1', '2', '3', 'A'},
  {'4', '5', '6', 'B'},
  {'7', '8', '9', 'C'},
  {'*', '0', '#', 'D'}
};

byte PINOS_LINHAS[LINHAS] = {36, 37, 38, 39}; // Pinos de conexão com as linhas do teclado
byte PINOS_COLUNAS[COLUNAS] = {12, 13, 15, 2}; // Pinos de conexão com as colunas do teclado

// Objeto global do teclado
Keypad teclado_personalizado = Keypad(makeKeymap(TECLAS_MATRIZ), PINOS_LINHAS, PINOS_COLUNAS, LINHAS, COLUNAS);

// ============================================================================
// Implementação das funções
// ============================================================================

void tecladoInit() {
  // Keypad já é inicializado globalmente
  // Esta função pode ser usada para configurações futuras
  Serial.println("✓ Teclado matricial inicializado");
}

char tecladoLerTecla() {
  return teclado_personalizado.getKey();
}

char tecladoAguardarTecla() {
  char tecla = 0;
  while (!tecla) {
    tecla = teclado_personalizado.getKey();
    delay(10); // Pequeno delay para não sobrecarregar
  }
  return tecla;
}

bool tecladoTeclaPressionada() {
  return (teclado_personalizado.getKey() != 0);
}