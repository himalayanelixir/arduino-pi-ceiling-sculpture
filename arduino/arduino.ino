// Copyright 2020 Harlen Bains
// Linted using cpplint
// Google C++ Style Guide https://google.github.io/styleguide/cppguide.html
#include <Servo.h>
#include <String.h>

// constants
#define DEBOUNCE_TIME .4
#define SAMPLE_FREQUENCY 20
#define MAXIMUM_DEBOUNCE (DEBOUNCE_TIME * SAMPLE_FREQUENCY)
#define MAXIMUM_NUMBER_OF_MOTORS 22
#define ARRAY_NUMBER 1
#define NUMBER_OF_MOTORS 2
#define NUMBER_OF_MOTORS_MOVING 1
#define TIMEOUT 50000
#define IGNORE_INPUT_TIME 150
#define MESSAGE_CHAR_LENGTH 300

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
char received_chars[MESSAGE_CHAR_LENGTH];
bool new_data = false;
// create servo objects
Servo my_servo[NUMBER_OF_MOTORS];
// create a array of ports with the order: motor, counter, reset
int ports[MAXIMUM_NUMBER_OF_MOTORS][3] = {
    {11, 12, 13}, {8, 9, 10}, {5, 6, 7}, {2, 3, 4}, {14, 15, 16}, {17, 18, 19},
    {20, 21, 22}, {23, 24, 25}, {29, 30, 31}, {35, 36, 37}, {41, 42, 43},
    {47, 48, 49}, {26, 27, 28}, {32, 33, 34}, {38, 39, 40}, {44, 45, 46},
    {50, 51, 52}, {53, 54, 55}, {56, 57, 58}, {59, 60, 61}, {63, 64, 65},
    {62, 66, 67}
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
// will range from 0 to the specified MAXIMUM_DEBOUNCE
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
  for (int i = 0; i < NUMBER_OF_MOTORS; i++) {
    // initialize all motor ports
    int x = ports[i][0];
    my_servo[i].attach(x);
    // initialize all counter ports  
    int y = ports[i][1];
    pinMode(y, INPUT_PULLUP);
    // initialize all reset ports
    int z = ports[i][2];
    pinMode(z, INPUT_PULLUP);
    // zero all motors and initialize reset variables
    my_servo[i].write(90);
    motor_sensor_counter1[i] = 1;
    motor_sensor_counter2[i] = 1;
    output[i] = 1;
    integrator[i] = MAXIMUM_DEBOUNCE;
    motor_commands[i][3] = IGNORE_INPUT_TIME;
  }
  Serial.print("<");
  Serial.print("Arduino is ready");
  Serial.print(" Array Number: ");
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

void RecvWithStartEndMarkers() {
  // handles the receiving of data over the serial port
  static bool receive_in_progress = false;
  static int char_count = 0;
  char start_marker = '<';
  char end_marker = '>';
  char receive_from_usb;
  while (Serial.available() > 0 && new_data == false) {
    receive_from_usb = Serial.read();
    if (receive_in_progress == true) {
      if (receive_from_usb != end_marker) {
        received_chars[char_count] = receive_from_usb;
        char_count++;
        if (char_count >= MESSAGE_CHAR_LENGTH) {
          char_count = MESSAGE_CHAR_LENGTH - 1;
        }
      } else {
        received_chars[char_count] = '\0';  // terminate the string
        receive_in_progress = false;
        char_count = 0;
        new_data = true;
      }
    } else if (receive_from_usb == start_marker) {
      receive_in_progress = true;
    }
  }
}

void Finished() {
  // sends message back to raspberry pi saying the command has been executed
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

void PopulateArray() {
  // fills array with instructions from the raspberry pi
  // temp string used to store the char array
  // easier to do opperations on string than chars
  String received_string = "";
  // give the string the value of the char array
  received_string = received_chars;
  // now lets populate the motor command array with values from the received
  // string
  for (int i = 0; i < NUMBER_OF_MOTORS; i++) {
    // we break everything in to pairs of values
    int search_1 = (i *2);
    int search_2 = ((i *2) + 1);

    String value_1 = GetValue(received_string, ',', search_1);
    String value_2 = GetValue(received_string, ',', search_2);

    if (value_1 == "Up") {
      motor_commands[i][0] = 1;
    } else if (value_1 == "Down") {
      motor_commands[i][0] = 2;
    } else {
      motor_commands[i][0] = 0;
    }
    motor_commands[i][1] = value_2.toInt();
  }
}

String GetValue(String data, char separator, int index) {
  // helps get a particular value from the incoming data string
  int found = 0;
  int string_index[] = { 0, -1 };
  int maximum_index = data.length() - 1;

  for (int i = 0; i <= maximum_index && found <= index; i++) {
    if (data.charAt(i) == separator || i == maximum_index) {
      found++;
      string_index[0] = string_index[1] + 1;
      string_index[1] = (i == maximum_index) ? i + 1 : i;
    }
  }
  return found > index ? data.substring(string_index[0], string_index[1]) : "";
}

void ProcessData() {
  // function that moves the motors and executes till they are done moving or
  // timeout
  while (go == true) {
    // initialize motors and get them moving
    for (int i = 0; i < NUMBER_OF_MOTORS; i++) {
      CountMoving();
      if (moving_motors < NUMBER_OF_MOTORS_MOVING &&
        motor_commands[i][2] != 1) {
        if (motor_commands[i][1] != 0) {
          StartMotors(i);
          motor_commands[i][2] = 1;
        }
      }
    }

    // subtract from motor rotations when a rotation is detected
    for (int i = 0; i < NUMBER_OF_MOTORS; i++) {
      if (motor_commands[i][2] == 1) {
        CheckCounter(i);
        // subtract from IGNORE_INPUT_TIME
        if (motor_commands[i][3] > 0) {
          motor_commands[i][3] = motor_commands[i][3] - 1;
        }
        // stop motors that have reached 0
        if (motor_commands[i][1] <= 0) {
          my_servo[i].write(90);
          motor_commands[i][2] = 0;
        }
      }

      // stop motors that have hit the reset
      // first stop the motor and then tell the code to move it down one
      // rotation
      if (digitalRead(ports[i][2]) == 0) {
        my_servo[i].write(110);
        motor_commands[i][0] = 2;
        motor_commands[i][1] = 1;
        motor_commands[i][2] = 0;
        // do not set ignore counter as we don't know excatly where it
        // stopped
        motor_commands[i][3] = IGNORE_INPUT_TIME;
      }
    }
    // see how many turns are left in the array
    // we want to zero it every time we recalculate the number of turns
    total_turns = 0;
    for (int i = 0; i < NUMBER_OF_MOTORS; i++) {
      total_turns += motor_commands[i][1];
    }
    // exit loop if there are no more motor rotations remaining
    if (total_turns <= 0) {
      go = false;
    }
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

int CountMoving() {
  // count the number of moving motors
  moving_motors = 0;
  for (int i = 0; i < NUMBER_OF_MOTORS; i++) {
    moving_motors += motor_commands[i][2];
  }
}

void CheckCounter(int i) {
  // check to see if we are on a rising edge
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

int CheckSwitch(int motor_number, int switchPort) {
  // check to see if the encoder switch is pressed or not
  /*Step 1: Update the integrator based on the input signal.  Note that the
  integrator follows the input, decreasing or increasing towards the limits
  as determined by the input state (0 or 1). */
  input[motor_number] = digitalRead(switchPort);

  if (input[motor_number] == 0) {
    if (integrator[motor_number] > 0)
      integrator[motor_number]--;
  } else {
    if (integrator[motor_number] < MAXIMUM_DEBOUNCE)
      integrator[motor_number]++;
  }
  /*Step 2: Update the output state based on the integrator.  Note that the
  output will only change states if the integrator has reached a limit,
  either 0 or MAXIMUM_DEBOUNCE. */
  if (integrator[motor_number] == 0) {
    previous_value[motor_number] = 0;
    return (0);
  } else if (integrator[motor_number] >= MAXIMUM_DEBOUNCE) {
    previous_value[motor_number] = 1;
    return (1);
  } else {
    return (previous_value[motor_number]);
  }
}

void StartMotors(int i) {
  // move motors
  if (motor_commands[i][0] == 1) {
    // Move up
    my_servo[i].write(80);
  } else if (motor_commands[i][0] == 2) {
    // Move down
    my_servo[i].write(110);
  } else {
    // Don't Move
    my_servo[i].write(90);
  }
}
