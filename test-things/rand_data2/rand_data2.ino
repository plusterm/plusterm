#include <math.h>

String out_str1;
String out_str2;

void setup() {
  Serial.begin(9600);
}

void loop() {
  int num1 = random(10);
  int num2 = random(-1,4);
  int num3 = random(-5,5);

  out_str1 = "param1: " + String(num1);
  Serial.println(out_str1);
  
  if (num2 > 0) {
    delay(random(0,500));
    out_str2 = "param2: " + String(num1 + num1*num3);
    Serial.println(out_str2);
  }
  delay(random(100,500));
}
