#include <Servo.h>
#include <String.h>

// constants
#define DEBOUNCE_TIME .4
#define SAMPLE_FREQUENCY 20
#define MAXIMUM (DEBOUNCE_TIME * SAMPLE_FREQUENCY)
#define NUMBER_MOTORS 10
#define NUMBER_MOTORS_MOVING 3
#define TIMEOUT 50000
#define IGNORE_INPUT_TIME 150

// function declarations
void RecvWithStartEndMarkers();
void Finished();
void PopulateArray();
String getValue();
void ProcessData();
int CountMoving();
void CheckCounter();
void StartMotors();
int CheckSwitch();
void StartMotors();

// variables for communication
const byte num_chars = 100;
char received_chars[num_chars];
bool new_data = false;
// create servo objects
Servo my_servo[NUMBER_MOTORS];
// create a array of ports with the order: motor, counter, reset
int ports[NUMBER_MOTORS][3] = {{26, 27, 28}, {32, 33, 34}, {38, 39, 40}, {44, 45, 46}, {50, 51, 52}, {53, 54, 55}, {56, 57, 58}, {59, 60, 61}, {63, 64, 65}, {62, 66, 67}};
// int ports[NUMBER_MOTORS][3] = {{11, 12, 13}, {8, 9, 10}, {2, 3, 4}, {14, 15, 16}, {17, 18, 19}, {20, 21, 22}, {23, 24, 25}, {29, 30, 31}, {35, 36, 37}};
// integer array that contains the direction and number of rotations a motor, and a flag that determines if it's moving, and another number that determines if we are ignoreing
// inputs from the switches or not
int motor_commands[NUMBER_MOTORS][4] = {0};
// array of new switch values
byte motor_sensor_counter1[NUMBER_MOTORS] = {0};
// array of old switch values
byte motor_sensor_counter2[NUMBER_MOTORS] = {0};
// Previous return value (CheckSwitch function)
int previous_value[NUMBER_MOTORS] = {1};
// 0 or 1 depending on the input signal
byte input[NUMBER_MOTORS] = {0};
// will range from 0 to the specified MAXIMUM
int integrator[NUMBER_MOTORS] = {0};
// cleaned-up version of the input signal
byte output[NUMBER_MOTORS] = {0};
// other variables needed for the ProcessData() function
bool go = true;
int total_turns = 0;
long timeout_counter = 0;
int moving_motors = 0;

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

  // zero all motors and initialize reset variables
  for (int i = 0; i < NUMBER_MOTORS; i++)
  {
    my_servo[i].write(90);
    motor_sensor_counter1[i] = 1;
    motor_sensor_counter2[i] = 1;
    output[i] = 1;
    integrator[i] = MAXIMUM;
    motor_commands[i][3] = IGNORE_INPUT_TIME;
  }

  Serial.println("");
  Serial.println("<");
  Serial.println("Arduino is ready");
  Serial.println(">");
}

void loop()
{
  // check to see if there is any new data
  //RecvWithStartEndMarkers();
  for (int i = 0; i < NUMBER_MOTORS; i++)
  {
    motor_commands[i][0] = 2;
    motor_commands[i][1] = 5;

  }

  go = true;
  ProcessData();
  Finished();
  delay(10000);

  for (int i = 0; i < NUMBER_MOTORS; i++)
  {
    motor_commands[i][0] = 1;
    motor_commands[i][1] = 100;

  }

  go = true;
  ProcessData();
  Finished();
  delay(10000);
}
