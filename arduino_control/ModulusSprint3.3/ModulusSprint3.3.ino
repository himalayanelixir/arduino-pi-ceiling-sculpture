#include <String.h>
#include <Servo.h>

#define DEBOUNCE_TIME    .5
#define SAMPLE_FREQUENCY  20
#define MAXIMUM     (DEBOUNCE_TIME * SAMPLE_FREQUENCY)

// function declarations
void RecvWithStartEndMarkers();
void ProcessData();
void ShowNewData();

// variables for communication
const byte numChars = 32;
char receivedChars[numChars];
bool newData = false;

// variables for motor 1
// ports
Servo myservo1;
byte motor_port = 3;
byte motor_counter_port = 4;
byte motor_reset_port = 2;
// motor info
String motor_direction = "";
byte motor_rotation_number = 0;
byte motor_sensor_counter1 = 0;
byte motor_sensor_counter2 = 0;
// 
// variables for motor 2
Servo myservo2;
byte motor_port2 = 9;
byte motor_counter_port2 = 8;
byte motor_reset_port2 = 7;
// motor info
String motor_direction2 = "";
byte motor_rotation_number2 = 0;
byte motor_sensor_counter12 = 0;
byte motor_sensor_counter22 = 0;
//
byte input;       /* 0 or 1 depending on the input signal */
int integrator;  /* Will range from 0 to the specified MAXIMUM */
byte output;      /* Cleaned-up version of the input signal */

byte input2;       /* 0 or 1 depending on the input signal */
int integrator2;  /* Will range from 0 to the specified MAXIMUM */
byte output2;      /* Cleaned-up version of the input signal */

//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

void ProcessData() {
  
  // variables
  String recievedString = "";
  String motor_rotation_string = "";
  String motor_rotation_string2 = "";
  // logic
  recievedString = receivedChars;
  motor_direction = getValue(recievedString, ',', 0);  
  motor_rotation_string = getValue(recievedString, ',', 1);
  motor_rotation_number = motor_rotation_string.toInt();

//
  motor_direction2 = getValue(recievedString, ',', 2);  
  motor_rotation_string2 = getValue(recievedString, ',', 3);
  motor_rotation_number2 = motor_rotation_string2.toInt();
//

  if (motor_direction == "Up") {
    myservo1.write(100);
  }
  else if (motor_direction == "Down") {
   myservo1.write(80);
  }

  else if (motor_direction == "None"){
    myservo1.write(90);
  }
  else if (motor_direction == "Reset"){
    Reset1();
  }
  else
  {
      // TODO: make this exit the program
      Serial.println("<");  
      Serial.print("Arduino: ");
      Serial.println("Invalid Input!");
  }
  
  while(true) {
    
    motor_sensor_counter2 = motor_sensor_counter1;
    checkswitch(motor_counter_port);
    motor_sensor_counter1 = output;
    delay(10);
    
    if(motor_rotation_number == 0) {
      myservo1.write(90);
      break;
    }
    
    if(digitalRead(motor_reset_port) == 0){
      myservo1.write(90);
      break;
    }
    
    if(motor_sensor_counter1 == 1 && motor_sensor_counter2 == 0) {
      motor_rotation_number--;
    }
  }

  if (motor_direction2 == "Up") {
    myservo2.write(100);
  }
  else if (motor_direction2 == "Down") {
   myservo2.write(80);
  }
  else if (motor_direction2 == "None"){
    myservo2.write(90);
  }
  else if (motor_direction2 == "Reset"){
    Reset2();
  }
  else
  {
      // TODO: make this exit the program
      Serial.println("<");  
      Serial.print("Arduino: ");
      Serial.println("Invalid Input!");
  }
  
  while(true) {
    
    motor_sensor_counter22 = motor_sensor_counter12;
    checkswitch2(motor_counter_port2);
    motor_sensor_counter12 = output2;
    delay(10);
    
    if(motor_rotation_number2 == 0) {
      myservo2.write(90);
      break;
    }
    
    if(digitalRead(motor_reset_port2) == 0){
      myservo2.write(90);
      break;
    }
    
    if(motor_sensor_counter12 == 1 && motor_sensor_counter22 == 0) {
      motor_rotation_number2--;
    }
  }
  
}

//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

void checkswitch(int switchPort) {
    /* Step 1: Update the integrator based on the input signal.  Note that the 
    integrator follows the input, decreasing or increasing towards the limits as 
    determined by the input state (0 or 1). */
    input = digitalRead(switchPort);

    if (input == 0)
        {
        if (integrator > 0)
        integrator--;
        }
    else if (integrator < MAXIMUM)
        integrator++;

    /* Step 2: Update the output state based on the integrator.  Note that the
    output will only change states if the integrator has reached a limit, either
    0 or MAXIMUM. */

    if (integrator == 0)
        output = 0;
    else if (integrator >= MAXIMUM)
        {
        output = 1;
        integrator = MAXIMUM;  /* defensive code if integrator got corrupted */
        }

    /********************************************************* End of debounce.c */
}

//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

void checkswitch2(int switchPort) {
    /* Step 1: Update the integrator based on the input signal.  Note that the 
    integrator follows the input, decreasing or increasing towards the limits as 
    determined by the input state (0 or 1). */
    input2 = digitalRead(switchPort);

    if (input2 == 0)
        {
        if (integrator2 > 0)
        integrator2--;
        }
    else if (integrator2 < MAXIMUM)
        integrator2++;

    /* Step 2: Update the output state based on the integrator.  Note that the
    output will only change states if the integrator has reached a limit, either
    0 or MAXIMUM. */

    if (integrator2 == 0)
        output2 = 0;
    else if (integrator2 >= MAXIMUM)
        {
        output2 = 1;
        integrator2 = MAXIMUM;  /* defensive code if integrator got corrupted */
        }

    /********************************************************* End of debounce.c */
}
