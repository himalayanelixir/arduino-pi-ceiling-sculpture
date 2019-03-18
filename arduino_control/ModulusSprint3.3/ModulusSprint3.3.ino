#include <String.h>
#include <Servo.h>

#define DEBOUNCE_TIME    .5
#define SAMPLE_FREQUENCY  20
#define MAXIMUM     (DEBOUNCE_TIME * SAMPLE_FREQUENCY)

#define NUMBER_MOTORS 4

// create a array of ports. Each line corresponds to the motor number starting from 0
// ie 0 is motor 1
// the order of the ports is motor, counter, reset
int ports[NUMBER_MOTORS][3] = {{2, 3, 4},{5, 6, 7}};
// initialize motors
Servo myServo[NUMBER_MOTORS];

void setup() {
  Serial.begin(9600);
  
  // initialize all motor ports
  Serial.println("Begining Initialization");
  Serial.print("Motor Ports: ");
  for (int i = 0; i < NUMBER_MOTORS; i++) {
    int x = ports[i][0];\
    Serial.print(x);
    Serial.print(" ");
    pinMode(x, OUTPUT);
  }

  // initialize all counter ports
  Serial.println("");
  Serial.print("Counter Ports: ");
  for (int i = 0; i < NUMBER_MOTORS; i++) {
    int x = ports[i][1];
    Serial.print(x);
    Serial.print(" ");
    pinMode(x, INPUT_PULLUP);
  }

  // initialize all reset ports
  Serial.println("");
  Serial.print("Reset Ports: ");
  for (int i = 0; i < NUMBER_MOTORS; i++) {
    int x = ports[i][2];
    Serial.print(x);
    Serial.print(" ");
    pinMode(x, INPUT_PULLUP);
  }
  Serial.println("");
  Serial.println("<");
  Serial.println("Arduino is ready");
  Serial.println(">");
}

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

byte input;       /* 0 or 1 depending on the input signal */
int integrator;  /* Will range from 0 to the specified MAXIMUM */
byte output;      /* Cleaned-up version of the input signal */

//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

void ProcessData() {

  // variables
  String recievedString = "";
  String motor_rotation_string = "";
  String motor_rotation_string2 = "";

  recievedString = receivedChars;

  // logic
  motor_direction = getValue(recievedString, ',', 0);
  motor_rotation_string = getValue(recievedString, ',', 1);
  motor_rotation_number = motor_rotation_string.toInt();

  //
  if (motor_direction == "Up") {
    myservo1.write(100);
  }
  else if (motor_direction == "Down") {
    myservo1.write(80);
  }

  else if (motor_direction == "None") {
    myservo1.write(90);
  }
  else if (motor_direction == "Reset") {
    Reset1();
  }
  else
  {
    // Sends Error Message
    Invalid();
  }

  // Print First Number
  Serial.println("---------");
  Serial.print("Motor 1: ");
  Serial.println(motor_rotation_number);

  while (true) {

    motor_sensor_counter2 = motor_sensor_counter1;
    checkswitch(motor_counter_port);
    motor_sensor_counter1 = output;
    delay(10);

    if (motor_rotation_number == 0) {
      myservo1.write(90);
      break;
    }

    if (digitalRead(motor_reset_port) == 0) {
      myservo1.write(90);
      break;
    }

    if (motor_sensor_counter1 == 1 && motor_sensor_counter2 == 0) {
      motor_rotation_number--;

      // Print Number Every Time It Changes
      Serial.print("Motor 1: ");
      Serial.println(motor_rotation_number);
    }
  }

  // Send Finished Signal
  Finished();

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

//void checkswitch2(int switchPort) {
//    /* Step 1: Update the integrator based on the input signal.  Note that the
//    integrator follows the input, decreasing or increasing towards the limits as
//    determined by the input state (0 or 1). */
//    input2 = digitalRead(switchPort);
//
//    if (input2 == 0)
//        {
//        if (integrator2 > 0)
//        integrator2--;
//        }
//    else if (integrator2 < MAXIMUM)
//        integrator2++;
//
//    /* Step 2: Update the output state based on the integrator.  Note that the
//    output will only change states if the integrator has reached a limit, either
//    0 or MAXIMUM. */
//
//    if (integrator2 == 0)
//        output2 = 0;
//    else if (integrator2 >= MAXIMUM)
//        {
//        output2 = 1;
//        integrator2 = MAXIMUM;  /* defensive code if integrator got corrupted */
//        }
//
//    /********************************************************* End of debounce.c */
//}
