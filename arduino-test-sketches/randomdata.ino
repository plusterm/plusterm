#include <math.h>

int x = 0;

void setup() {
  Serial.begin(9600);
}

void loop() {
  int num1 = random(100);
  int num2 = random(-1,2);
  
  if (Serial.available()) {
    char inChar = (char)Serial.read();

    switch (inChar) {
      case 'r': 
      Serial.print("Reading:");
      Serial.println(num1);
      break;

    case 's': 
      Serial.print("x:");
      Serial.print(x);
      Serial.print(",y:");
      Serial.println(x % 10 + num1*num2);
      x++;
      break;
    }
  }
}
