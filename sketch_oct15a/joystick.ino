// // Pinos analógicos da ESP32
// int JoyStick_X = 32; // X-axis (ADC1_6)
// int JoyStick_Y = 33; // Y-axis (ADC1_7)
// int Button = 36;      // botão (digital)

// // Configuração inicial
// void setup() {
//   pinMode(JoyStick_X, INPUT);
//   pinMode(JoyStick_Y, INPUT);
//   pinMode(Button, INPUT_PULLUP);  // usa pull-up interno
//   Serial.begin(9600);
// }

// // Loop principal
// void loop() {
//   // Leitura analógica (0–4095)
//   int xRaw = analogRead(JoyStick_X);
//   int yRaw = analogRead(JoyStick_Y);

//   // Converte para tensão (0–3.3 V)
//   float xVolt = xRaw * (3.3 / 4095.0);
//   float yVolt = yRaw * (3.3 / 4095.0);

//   // Leitura do botão (ativo em LOW)
//   int buttonState = digitalRead(Button);

//   // Saída serial
//   Serial.print("X: "); Serial.print(xVolt, 2); Serial.print(" V, ");
//   Serial.print("Y: "); Serial.print(yVolt, 2); Serial.print(" V, ");
//   Serial.print("Button: ");
//   Serial.println(buttonState == HIGH ? "not pushed" : "pushed");

//   delay(200);
// }
