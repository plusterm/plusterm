#include <math.h>

String deg_str;
String sin_str;

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

    deg_str = "Degrees: " + String(deg) + ", ";
    sin_str = "Sinus: " + String(sinus);
    Serial.println(deg_str + sin_str);
    
     deg += 2;
     if (deg == 360) {
      deg = 0;
     }
     delay(200);
  }
}
