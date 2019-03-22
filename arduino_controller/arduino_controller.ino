#include <String.h>
#include <Servo.h>

#define DEBOUNCE_TIME    .5
#define SAMPLE_FREQUENCY  20
#define MAXIMUM     (DEBOUNCE_TIME * SAMPLE_FREQUENCY)

#define NUMBER_MOTORS 2

// function declarations
void RecvWithStartEndMarkers();
void ProcessData();
void ShowNewData();

// variables for communication
const byte numChars = 32;
char receivedChars[numChars];
bool newData = false;

// initialize motors
Servo myServo[NUMBER_MOTORS];
// create a array of ports. Each line corresponds to the motor number starting from 0.
// the order of the ports is motor, counter, reset
int ports[NUMBER_MOTORS][3] = {{2, 3, 4},{5, 6, 7}};

String motor_direction[NUMBER_MOTORS] = {""};;
byte motor_rotation_number[NUMBER_MOTORS] = {0};
byte motor_sensor_counter1[NUMBER_MOTORS] = {0};;
byte motor_sensor_counter2[NUMBER_MOTORS] = {0};;

// 0 or 1 depending on the input signal
byte input[NUMBER_MOTORS] = {0};
// will range from 0 to the specified MAXIMUM 
int integrator[NUMBER_MOTORS] = {0};
// cleaned-up version of the input signal
byte output[NUMBER_MOTORS]= {0};;      

void setup() {
  Serial.begin(9600);
  
  // initialize all motor ports
  Serial.println("Begining Initialization");
  Serial.print("Motor Ports: ");
  for (int i = 0; i < NUMBER_MOTORS; i++) {
    int x = ports[i][0];\
    Serial.print(x);
    Serial.print(" ");
    myServo[i].attach(x);
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

void loop() {
  RecvWithStartEndMarkers();
  ShowNewData();
}

