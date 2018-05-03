#include "CRC32.h"

/* This program was designed to test the packet loss detector
 * module in Plusterm. It compares recieved data to a CRC32
 * checksum to see if it matches the string "plus".
 * It then returns "fail|match,pole" depending on if matched or not.
 * 
 * If the debug bool is True then it produces some errors for the
 * module to detect.
 */
 
bool debug = true;

int errorVal1 = 3;
int errorVal2 = 2;

String inString;
bool match;


void setup()
{
  // Begin serial output for testing / debugging.
  Serial.begin(9600);
  Serial.setTimeout(100);
}

void loop()
{
  // The known CRC32 Checksum for the "plus" string below.
  const uint32_t KNOWN_CHECKSUM = 0x4297105A;
  String inString = "";

  int debug_rand1 = random(100);
  int debug_rand2 = random(100);

  // Produce errors in 3% of indata
  if (debug == true)
  {
    int debug_rand1 = random(100);
    int debug_rand2 = random(100);

    if (debug_rand1 < 3)
    {
      inString = "a";
    }
    
  }

  if (Serial.available())
  {
    while (Serial.available()) {
      delay(2);  //delay to allow byte to arrive in input buffer
      char c = Serial.read();

      // avoid CR and NL
      if (c != '\r'&& c != '\n')
      {
      inString += c;
      }
    }
    
    if (inString.length() >0)
    {
      // Serial.println(inString);
      
      int numChars = inString.length();
      uint8_t byteBuffer[numChars];
      
      for (int i = 0; i < numChars; i++)
      {
        byteBuffer[i] = uint8_t(inString[i]);
      }
      
      // Calculate the checksum for the whole buffer.    
      uint32_t checksum = CRC32::calculate(byteBuffer, numChars - 1);
      
      //Serial.println(checksum);
    
      if (checksum == KNOWN_CHECKSUM)
      {
        // Produce errors when indata was correct
        if (debug == true && debug_rand2 < errorVal2)
        {
          Serial.println("match,pol");
        }
        else if (debug == true && debug_rand2 > 100 - errorVal1)
        {
          Serial.println("atch,pole");
        }
        else if (debug == true && debug_rand2 == 100 - errorVal1)
        {
          Serial.println("matchpole");
        }
        else
        {
          Serial.println("match,pole");
        }
      }
      else
      {
        // Produce errors in errorVal2/2 % of outdata when indata was incorrect
        if (debug == true && debug_rand2 >= 50)
        {
          Serial.println("fail,pol");
        }
        else
        {
          Serial.println("fail,pole");
        }
      }
    }
  }
}
