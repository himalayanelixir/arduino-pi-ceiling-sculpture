
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

#define SERVOSPEED  150

const byte numChars = 32;
char receivedChars[numChars];

boolean newData = false;

int sensorPin = A0;  

void setup() {
    Serial.begin(9600);
    Serial.println("<Arduino is ready>");


    pwm.begin();
    pwm.setPWMFreq(60);
    delay(10);
}

void loop() {
    recvWithStartEndMarkers();
    showNewData();
}

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

void processData() {
    if (strcmp(receivedChars,"Up")==0)
      {
        Serial.println("<");  
        Serial.print("Arduino: ");
        Serial.println("Moving Up!");
        pwm.setPWM(0, 0, 325);
      }
    else if (strcmp(receivedChars,"Down")==0)
    {
        Serial.println("<");  
        Serial.print("Arduino: ");
        Serial.println("Moving Down!");
        pwm.setPWM(0, 0, 350);
    }
    else if (strcmp(receivedChars,"Stop")==0)
    {
        Serial.println("<");  
        Serial.print("Arduino: ");
        Serial.println("Moving Stopping!");
        pwm.setPWM(0, 0, 4096);
    }
    else
    {
        Serial.println("<");  
        Serial.print("Arduino: ");
        Serial.println("Invalid Input!");
    }
}
void showNewData() {
    if (newData == true) {
        processData();  
        //Serial.print("Arduino: ");
        //Serial.println(receivedChars);
        Serial.println(">");
        newData = false;
    }
}

