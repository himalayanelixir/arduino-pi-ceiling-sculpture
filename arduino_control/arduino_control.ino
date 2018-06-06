// constants
#define NUMBER_OF_MOTORS 2
#define UP_SPEED 295
#define DOWN_SPEED 270
#define STOP_SPEED 0

// libraries
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
#include <String.h> 
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

// variables
const byte numChars = 32;
char receivedChars[numChars];

boolean newData = false;

String recievedString = "";
int sensor_value1[NUMBER_OF_MOTORS];
int sensor_value2[NUMBER_OF_MOTORS];
int rotation_int[NUMBER_OF_MOTORS];
String rotation_direction[NUMBER_OF_MOTORS];

// motor pins
int m1_sensor_pin = A0; 
int m2_sensor_pin = A0; 

String m1_rotation = "";
String m2_rotation = "";


void setup() {
    // set array values
    memset(sensor_value1, 0, sizeof(sensor_value1));
    memset(sensor_value2, 0, sizeof(sensor_value2));

    for (int i=0; i<NUMBER_OF_MOTORS; i++) {
      rotation_direction[i] = "";
    }

    // setup serial monitor
    Serial.begin(9600);
    
    // setup pwm shield
    pwm.begin();
    pwm.setPWMFreq(50);
    delay(100);
    pwm.setPWM(0, 0, 0);

    // alert user
    Serial.println("<Arduino is ready>");
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
  
  rotation_direction[0] = getValue(recievedString, ',', 0);  
  m1_rotation = getValue(recievedString, ',', 1);
  rotation_int[0] = m1_rotation.toInt();

  rotation_direction[1] = getValue(recievedString, ',', 2);  
  m2_rotation = getValue(recievedString, ',', 3);
  rotation_int[1] = m2_rotation.toInt();

  
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

 
  
  if (rotation_direction[0] == "Up") {
    Serial.println("<");  
    Serial.print("Arduino: ");
    Serial.println("Moving Up!");
    upMotor(0);
    while (1) {
      readValues();
      Serial.println(sensor_value2[0]);
      if (sensor_value1[0] < 500 && sensor_value2[0] > 500){
          rotation_int[0] = rotation_int[0] - 1;
      }

      if (rotation_int[0] == 0){
        break;
      }
     delay(500);
    }
   stopMotor(0);
  }
  else if (rotation_direction[0] == "Down") {
    Serial.println("<");  
    Serial.print("Arduino: ");
    Serial.println("Moving Down!");
    downMotor(0);
    while (1) {
      readValues();
      Serial.println(sensor_value2[0]);
      if (sensor_value1[0] < 500 && sensor_value2[0] > 500){
          rotation_int[0] = rotation_int[0] - 1;
      }

      if (rotation_int[0] == 0){
        break;
      }
     delay(500);
    }
   stopMotor(0);
  }

  else if (rotation_direction[0] == "Stop"){
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
  sensor_value1[0] = sensor_value2[0];
  sensor_value2[0] = analogRead(m1_sensor_pin); 
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

