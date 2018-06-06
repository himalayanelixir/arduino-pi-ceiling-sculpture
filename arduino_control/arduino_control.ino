
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
#include <String.h> 

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

#define SERVOSPEED  150

const byte numChars = 32;
char receivedChars[numChars];

boolean newData = false;

String recievedString = "";

int number_of_motors = 2;
//int rotation_int[number_of_motors];
// motor 1 variables
int m1_sensor_pin = A0;  
int m1_sensor_value1 = 0;
int m1_sensor_value2 = 0;
int m1_rotation_int = 0;
String m1_rotation_direction = "";
String m1_rotation = "";

int m2_sensor_pin = A0;  
int m2_sensor_value1 = 0;
int m2_sensor_value2 = 0;
int m2_rotation_int = 0;
String m2_rotation_direction = "";
String m2_rotation = "";

void setup() {
    Serial.begin(9600);
    Serial.println("<Arduino is ready>");

    pwm.begin();
    pwm.setPWMFreq(50);
    delay(10);
    pwm.setPWM(0, 0, 0);
}

void loop() {
    recvWithStartEndMarkers();
    showNewData();
}

//////////////////////////////////////
//////////////////////////////////////
//////////////////////////////////////

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
  
  
  recievedString = receivedChars;
  
  m1_rotation_direction = getValue(recievedString, ',', 0);  
  m1_rotation = getValue(recievedString, ',', 1);
  m1_rotation_int = m1_rotation.toInt();

  m2_rotation_direction = getValue(recievedString, ',', 2);  
  m2_rotation = getValue(recievedString, ',', 3);
  m2_rotation_int = m2_rotation.toInt();

  
  //serial print info
  Serial.println("<"); 
  Serial.print("RevievedString: ");
  Serial.println(recievedString);
  Serial.println("Number of Rotations: ");
  Serial.print("m1: ");
  Serial.println(m1_rotation);
  Serial.print("m2: ");
  Serial.println(m2_rotation);


  // while all motors aren't ready

 
  
  if (m1_rotation_direction == "Up") {
    Serial.println("<");  
    Serial.print("Arduino: ");
    Serial.println("Moving Up!");
    upMotor(0);
    while (1) {
      readValues();
      Serial.println(m1_sensor_value2);
      if (m1_sensor_value1 < 500 && m1_sensor_value2 > 500){
          m1_rotation_int = m1_rotation_int - 1;
      }

      if (m1_rotation_int == 0){
        break;
      }
     delay(500);
    }
   stopMotor(0);
  }
  else if (m1_rotation_direction == "Down") {
    Serial.println("<");  
    Serial.print("Arduino: ");
    Serial.println("Moving Down!");
    downMotor(0);
    while (1) {
      readValues();
      Serial.println(m1_sensor_value2);
      if (m1_sensor_value1 < 500 && m1_sensor_value2 > 500){
          m1_rotation_int = m1_rotation_int - 1;
      }

      if (m1_rotation_int == 0){
        break;
      }
     delay(500);
    }
   stopMotor(0);
  }

  else if (m1_rotation_direction == "Stop"){
      Serial.println("<");  
      Serial.print("Arduino: ");
      Serial.println("Moving Stopping!");
      stopMotor(0);
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

void readValues() {
  m1_sensor_value1 = m1_sensor_value2;
  m1_sensor_value2 = analogRead(m1_sensor_pin); 
}

String getValue(String data, char separator, int index)
{
    int found = 0;
    int strIndex[] = { 0, -1 };
    int maxIndex = data.length() - 1;

    for (int i = 0; i <= maxIndex && found <= index; i++) {
        if (data.charAt(i) == separator || i == maxIndex) {
            found++;
            strIndex[0] = strIndex[1] + 1;
            strIndex[1] = (i == maxIndex) ? i+1 : i;
        }
    }
    return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}

