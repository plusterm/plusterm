#include <math.h>

void setup() {
  Serial.begin(9600);
}

void loop() {
  int num1 = random(10);
  int num2 = random(-1,4);
  int num3 = random(-5,5);

  Serial.print("param1: ");
  Serial.print(num1);
  Serial.print('\n');
  if (num2 > 0) {
    delay(random(0,500));
    Serial.print("param2: ");
    Serial.print(num1 + num1*num3);
    Serial.print('\n');
  }
  delay(random(0,500));
}
