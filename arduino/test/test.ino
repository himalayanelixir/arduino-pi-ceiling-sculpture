// Copyright 2020 Harlen Bains
// Linted using cpplint
// Google C++ Style Guide https://google.github.io/styleguide/cppguide.html
#include <Servo.h>
#include <String.h>

// constants
#define DEBOUNCE_TIME .4
#define SAMPLE_FREQUENCY 20
#define MAXIMUM (DEBOUNCE_TIME * SAMPLE_FREQUENCY)
#define ARRAY_NUMBER 0
#define NUMBER_OF_MOTORS 1
#define NUMBER_OF_MOTORS_MOVING 1
#define TIMEOUT 50000
#define IGNORE_INPUT_TIME 150

// function declarations
void RecvWithStartEndMarkers();
void Finished();
void PopulateArray();
String GetValue();
void ProcessData();
int CountMoving();
void CheckCounter();
void StartMotors();
int CheckSwitch();
void StartMotors();

// variables for communication
// const byte num_chars = 100;
// char received_chars[num_chars];
char received_chars[300];
bool new_data = false;
// create servo objects
Servo my_servo[NUMBER_OF_MOTORS];
// create a array of ports with the order: motor, counter, reset
int ports[NUMBER_OF_MOTORS][3] = {
    { 8, 9, 10 }
};
// integer array that contains the direction and number of rotations a motor,
// and a flag that determines if it's moving, and another number that determines
// if we are ignoreing inputs from the switches or not
int motor_commands[NUMBER_OF_MOTORS][4] = { 0 };
// array of new switch values
byte motor_sensor_counter1[NUMBER_OF_MOTORS] = { 0 };
// array of old switch values
byte motor_sensor_counter2[NUMBER_OF_MOTORS] = { 0 };
// Previous return value (CheckSwitch function)
int previous_value[NUMBER_OF_MOTORS] = { 1 };
// 0 or 1 depending on the input signal
byte input[NUMBER_OF_MOTORS] = { 0 };
// will range from 0 to the specified MAXIMUM
int integrator[NUMBER_OF_MOTORS] = { 0 };
// cleaned-up version of the input signal
byte output[NUMBER_OF_MOTORS] = { 0 };
// other variables needed for the ProcessData() function
bool go = true;
int total_turns = 0;
int timeout_counter = 0;
int moving_motors = 0;
bool did_timeout = false;

void setup() {
  // setup serial port
  Serial.begin(9600);
  // initialize all motor ports
  Serial.println("Begining Initialization");
  Serial.print("Motor Ports: ");
  for (int i = 0; i < NUMBER_OF_MOTORS; i++) {
    int x = ports[i][0];
    Serial.print(x);
    Serial.print(" ");
    my_servo[i].attach(x);
  }
  // initialize all counter ports
  Serial.println("");
  Serial.print("Counter Ports: ");
  for (int i = 0; i < NUMBER_OF_MOTORS; i++) {
    int x = ports[i][1];
    Serial.print(x);
    Serial.print(" ");
    pinMode(x, INPUT_PULLUP);
  }
  // initialize all reset ports
  Serial.println("");
  Serial.print("Reset Ports: ");
  for (int i = 0; i < NUMBER_OF_MOTORS; i++) {
    int x = ports[i][2];
    Serial.print(x);
    Serial.print(" ");
    pinMode(x, INPUT_PULLUP);
  }
  // zero all motors and initialize reset variables
  for (int i = 0; i < NUMBER_OF_MOTORS; i++) {
    my_servo[i].write(90);
    motor_sensor_counter1[i] = 1;
    motor_sensor_counter2[i] = 1;
    output[i] = 1;
    integrator[i] = MAXIMUM;
    motor_commands[i][3] = IGNORE_INPUT_TIME;
  }
  Serial.print("<");
  Serial.print("Arduino is ready");
  Serial.print("Array Number: ");
  Serial.print(ARRAY_NUMBER);
  Serial.print(" Number of Motors: ");
  Serial.print(NUMBER_OF_MOTORS);
  Serial.print(">");
}

void loop() {
  // check to see if there is any new data
  RecvWithStartEndMarkers();
  // if there is new data process it
  if (new_data == true) {
    new_data = false;
    go = true;
    did_timeout = false;
    timeout_counter = 0;
    Serial.print("<");
    PopulateArray();
    ProcessData();
    Finished();
  }
}

//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

// handles the receiving of data over the serial port
void RecvWithStartEndMarkers() {
  static boolean recvInProgress = false;
  static byte ndx = 0;
  char startMarker = '<';
  char endMarker = '>';
  char rc;

  while (Serial.available() > 0 && new_data == false) {
    rc = Serial.read();

    if (recvInProgress == true) {
      if (rc != endMarker) {
        received_chars[ndx] = rc;
        ndx++;
        if (ndx >= num_chars) {
          ndx = num_chars - 1;
        }
      } else {
        received_chars[ndx] = '\0';  // terminate the string
        recvInProgress = false;
        ndx = 0;
        new_data = true;
      }
    } else if (rc == startMarker) {
      recvInProgress = true;
    }
  }
}

// sends message back to raspberry pi saying the command has been executed
void Finished() {
  if (did_timeout == true) {
    Serial.print("\033[31m");
    Serial.print("RECIEVED: TIMEOUT");
    Serial.print(" - MOTOR(S): ");
    for (int i = 0; i < NUMBER_OF_MOTORS; i++) {
      if (motor_commands[i][1] != 0) {
        Serial.print(i);
        Serial.print(" ");
      }
    }
    Serial.print("\033[0m");
    Serial.print(">");
  } else {
    Serial.print("\033[32m");
    Serial.print("RECIEVED: DONE");
    Serial.print("\033[0m");
    Serial.print(">");
  }
  for (int i = 0; i < NUMBER_OF_MOTORS; i++) {
    my_servo[i].write(90);
    motor_commands[i][0] = 0;
    motor_commands[i][1] = 0;
    motor_commands[i][2] = 0;
    motor_commands[i][3] = IGNORE_INPUT_TIME;
  }
}

// fills array with instructions from the raspberry pi
void PopulateArray() {
  // temp string used to store the char array
  // easier to do opperations on string than chars
  String received_string = "";
  // give the string the value of the char array
  received_string = received_chars;

  // now lets populate the motor command array with values from the received
  // string
  for (int i = 0; i < NUMBER_OF_MOTORS; i++) {
    // we break everything in to pairs of values
    int search1 = (i *2);
    int search2 = ((i *2) + 1);

    String value1 = GetValue(received_string, ',', search1);
    String value2 = GetValue(received_string, ',', search2);

    if (value1 == "Up") {
      motor_commands[i][0] = 1;
    } else if (value1 == "Down") {
      motor_commands[i][0] = 2;
    } else if (value1 == "None") {
      motor_commands[i][0] = 0;
    } else if (value1 == "Reset") {
      motor_commands[i][0] = 3;
    } else {
      // Sends Error Message
    }

    motor_commands[i][1] = value2.toInt();
  }
}

// helps get a particular value from the incoming data string
String GetValue(String data, char separator, int index) {
  int found = 0;
  int strIndex[] = { 0, -1 };
  int maxIndex = data.length() - 1;

  for (int i = 0; i <= maxIndex && found <= index; i++) {
    if (data.charAt(i) == separator || i == maxIndex) {
      found++;
      strIndex[0] = strIndex[1] + 1;
      strIndex[1] = (i == maxIndex) ? i + 1 : i;
    }
  }
  return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}

//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

// function that moves the motors and executes till they are done moving or
// timeout
void ProcessData() {
  while (go == true) {
    go = false;
    // turn the LED on (HIGH is the voltage level)
    digitalWrite(LED_BUILTIN, HIGH);
    // wait for 5 seconds
    delay(5000);
     // turn the LED off by making the voltage LOW
    digitalWrite(LED_BUILTIN, LOW);

    // turn the LED on (HIGH is the voltage level)
    digitalWrite(LED_BUILTIN, HIGH);
    // wait for half a seconds
    delay(50);
    // turn the LED off by making the voltage LOW
    digitalWrite(LED_BUILTIN, LOW);
    // wait for half a seconds
    delay(50);
    timeout_counter = timeout_counter + 1;
    // time out loop if stall
    if (timeout_counter >= TIMEOUT) {
      go = false;
      did_timeout = true;
      for (int i = 0; i < NUMBER_OF_MOTORS; i++) {
      my_servo[i].write(90);
      }
    }
  }
}

// count the number of moving motors
int CountMoving() {
  moving_motors = 0;
  for (int i = 0; i < NUMBER_OF_MOTORS; i++) {
    moving_motors += motor_commands[i][2];
  }
}

// check to see if we are on a rising edge
void CheckCounter(int i) {
  motor_sensor_counter2[i] = motor_sensor_counter1[i];
  motor_sensor_counter1[i] = CheckSwitch(i, ports[i][1]);
  if (motor_commands[i][0] == 1) {
    if (motor_sensor_counter1[i] == 1 && motor_sensor_counter2[i] == 0) {
      if (motor_commands[i][3] == 0) {
        motor_commands[i][1] = motor_commands[i][1] - 1;
      }
    }
  } else {
    if (motor_sensor_counter1[i] == 0 && motor_sensor_counter2[i] == 1) {
      if (motor_commands[i][3] == 0) {
        motor_commands[i][1] = motor_commands[i][1] - 1;
      }
    }
  }
  if (motor_commands[i][1] < 0) {
    motor_commands[i][1] = 0;
  }
}

// check to see if the encoder switch is pressed or not
int CheckSwitch(int motor_number, int switchPort) {
  /*Step 1: Update the integrator based on the input signal.  Note that the
  integrator follows the input, decreasing or increasing towards the limits
  as determined by the input state (0 or 1). */
  input[motor_number] = digitalRead(switchPort);

  if (input[motor_number] == 0) {
    if (integrator[motor_number] > 0)
      integrator[motor_number]--;
  } else {
    if (integrator[motor_number] < MAXIMUM)
      integrator[motor_number]++;
  }

  /*Step 2: Update the output state based on the integrator.  Note that the
  output will only change states if the integrator has reached a limit,
  either 0 or MAXIMUM. */

  if (integrator[motor_number] == 0) {
    previous_value[motor_number] = 0;
    return (0);
  } else if (integrator[motor_number] >= MAXIMUM) {
    previous_value[motor_number] = 1;
    return (1);
  } else {
    return (previous_value[motor_number]);
  }
}

// move motors
void StartMotors(int i) {
  if (motor_commands[i][0] == 1) {
    // Move up
    my_servo[i].write(80);
  } else if (motor_commands[i][0] == 2) {
    // Move down
    my_servo[i].write(110);
  } else if (motor_commands[i][0] == 0) {
    // Don't Move
    my_servo[i].write(90);
  } else if (motor_commands[i][0] == 3) {
    // Move Up for Reset
    my_servo[i].write(80);
  } else {
    // Don't Move
    my_servo[i].write(90);
  }
}
