#include <math.h>

float DegToRad(int deg) {
  return deg * (PI / 180);
}

void setup() {
  Serial.begin(9600);
  delay(100);
}

void loop() {
  int deg = 0;
  float sinus = 0;
  
  while (true) {
    float radian = DegToRad(deg);
    sinus = sin(radian);
    
    Serial.print("Degrees: ");
    Serial.print(deg);
    Serial.print(",");
    Serial.print("Sinus value: ");
    Serial.print(sinus);
    Serial.print("\n");
    Serial.println(deg);
    
     deg += 2;
     if (deg == 360) {
      deg = 0;
     }
     delay(200);
  }
}
