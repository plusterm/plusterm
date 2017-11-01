#include <math.h>

float DegToRad(int deg) {
  return deg * (PI / 180);
}

void setup() {
  Serial.begin(9600);
}

void loop() {
  int deg = 0;
  float sinus = 0;
  
  while (true) {
    float radian = DegToRad(deg);
    sinus = sin(radian);
    Serial.print(deg);
    Serial.print(",");
    Serial.print(sinus);
    Serial.print("\n");
    delay(100);
    deg++;
  }

}
