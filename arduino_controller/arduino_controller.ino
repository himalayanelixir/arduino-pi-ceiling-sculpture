#include <Servo.h>
#include <String.h>

// constants
#define DEBOUNCE_TIME .4
#define SAMPLE_FREQUENCY 20
#define MAXIMUM (DEBOUNCE_TIME * SAMPLE_FREQUENCY)
#define NUMBER_MOTORS 2
#define TIMEOUT 10000

// function declarations`
void RecvWithStartEndMarkers();
void ProcessData();
int CheckSwitch();
void PopulateArray();

// variables for communication
const byte num_chars = 100;
char received_chars[num_chars];
bool new_data = false;

// initialize motors
Servo my_servo[NUMBER_MOTORS];
// create a array of ports with the order: motor, counter, reset
// int ports[NUMBER_MOTORS][3] = {{62, 66, 67}};
int ports[NUMBER_MOTORS][3] = {{2, 3, 4}, {5, 6, 7}};
// integer array that contains the direction and number of rotations a motor
// needs to go
int motor_commands[NUMBER_MOTORS][2] = {0};

// array of new switch values
byte motor_sensor_counter1[NUMBER_MOTORS] = {0};

// array of old switch values
byte motor_sensor_counter2[NUMBER_MOTORS] = {0};

// 0 or 1 depending on the input signal
byte input[NUMBER_MOTORS] = {0};
// will range from 0 to the specified MAXIMUM
int integrator[NUMBER_MOTORS] = {MAXIMUM};
// cleaned-up version of the input signal
byte output[NUMBER_MOTORS] = {0};

void setup()
{
  // setup serial port
  Serial.begin(9600);

  // initialize all motor ports
  Serial.println("Begining Initialization");
  Serial.print("Motor Ports: ");
  for (int i = 0; i < NUMBER_MOTORS; i++)
  {
    int x = ports[i][0];
    Serial.print(x);
    Serial.print(" ");
    my_servo[i].attach(x);
  }

  // initialize all counter ports
  Serial.println("");
  Serial.print("Counter Ports: ");
  for (int i = 0; i < NUMBER_MOTORS; i++)
  {
    int x = ports[i][1];
    Serial.print(x);
    Serial.print(" ");
    pinMode(x, INPUT_PULLUP);
  }

  // initialize all reset ports
  Serial.println("");
  Serial.print("Reset Ports: ");
  for (int i = 0; i < NUMBER_MOTORS; i++)
  {
    int x = ports[i][2];
    Serial.print(x);
    Serial.print(" ");
    pinMode(x, INPUT_PULLUP);
  }

  // zero all motors
  for (int i = 0; i < NUMBER_MOTORS; i++)
  {
    my_servo[i].write(90);
  }

  Serial.println("");
  Serial.println("<");
  Serial.println("Arduino is ready");
  Serial.println(">");
}

void loop()
{
  // check to see if there is any new data
  RecvWithStartEndMarkers();

  // if there is new data process it
  if (new_data == true)
  {
    new_data = false;
    Serial.println("<");
    Serial.print("Arduino: ");
    Serial.println(received_chars);
    ProcessData();
  }
}
