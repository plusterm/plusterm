int i_b = 0;
int i_t = 0;
String outString;

void setup() {
  Serial.begin(9600);
  delay(100);
}

void loop() {
  if (Serial.available()) {
    String inString = Serial.readString();
    if (inString.equals("btn\r\n")) { 
      outString = "GUI:drawbutton(button" + String(i_b) + ", label" + String(i_b) + ")\n";
      Serial.print(outString);
      i_b += 1;
    }
    else if (inString.equals("txt\r\n")) {
      outString = "GUI:showtext(Some text " + String(i_t) + ")\n";
      Serial.print(outString);
      i_t += 1;
    }
  }
}
