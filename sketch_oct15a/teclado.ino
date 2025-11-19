// #include <Keypad.h> // Biblioteca do código

// const byte LINHAS = 4; // Linhas do teclado
// const byte COLUNAS = 4; // Colunas do teclado

// const char TECLAS_MATRIZ[LINHAS][COLUNAS] = { // Matriz de caracteres (mapeamento do teclado)
//   {'1', '2', '3', 'A'},
//   {'4', '5', '6', 'B'},
//   {'7', '8', '9', 'C'},
//   {'*', '0', '#', 'D'}
// };

// // ⚠️ Remova o const daqui:
// byte PINOS_LINHAS[LINHAS] = {17, 15, 13, 12}; // Pinos de conexão com as linhas do teclado
// byte PINOS_COLUNAS[COLUNAS] = {33, 25, 26, 27}; // Pinos de conexão com as colunas do teclado

// Keypad teclado_personalizado = Keypad(makeKeymap(TECLAS_MATRIZ), PINOS_LINHAS, PINOS_COLUNAS, LINHAS, COLUNAS); // Inicia teclado

// void setup() {
//   Serial.begin(9600); // Inicia porta serial
// }

// void loop() {
//   char leitura_teclas = teclado_personalizado.getKey(); // Atribui a variável a leitura do teclado

//   if (leitura_teclas) { // Se alguma tecla foi pressionada
//     Serial.println(leitura_teclas); // Imprime a tecla pressionada na porta serial
//   }
// }