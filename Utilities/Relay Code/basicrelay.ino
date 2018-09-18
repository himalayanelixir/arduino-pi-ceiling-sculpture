#include <String.h> 

// variables
const byte numChars = 32;
char receivedChars[numChars];
boolean newData = false;

void setup() {
  // put your setup code here, to run once:
    Serial.begin(9600);
    Serial.println("<Arduino is ready>");
    Serial.println(">");
}

void loop() {
  // put your main code here, to run repeatedly:
    recvWithStartEndMarkers();
    showNewData();
}

//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

void recvWithStartEndMarkers() {
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;
 
    while (Serial.available() > 0 && newData == false) {
        rc = Serial.read();

        if (recvInProgress == true) {
            if (rc != endMarker) {
                receivedChars[ndx] = rc;
                ndx++;
                if (ndx >= numChars) {
                    ndx = numChars - 1;
                }
            }
            else {
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                newData = true;
            }
        }

        else if (rc == startMarker) {
            recvInProgress = true;
        }
    }
}

//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

void showNewData() {
  if (newData == true) {
      //processData();  
      Serial.print("Arduino: ");
      Serial.println(receivedChars);
      Serial.println(">");
      newData = false;
  }
}