#include <math.h>

float DegToRad(int deg) {
  return deg * (PI / 180);
}

void setup() {
  Serial.begin(9600);
  delay(100);
}

String deg_str, sin_str, print_str;

void loop() {
  int deg = 0;
  float sinus = 0;
  
  while (true) {
    float radian = DegToRad(deg);
    sinus = sin(radian);
    
    deg_str = String("Degrees: " + String(deg));
    sin_str = String("Sinus: " + String(sinus));
    print_str = deg_str + ", " + sin_str;
    Serial.println(print_str);
   
     deg += 2;
     if (deg == 360) {
      deg = 0;
     }
     delay(100);
  }
}
