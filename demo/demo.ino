// constants
#define NUMBER_OF_MOTORS 1
#define UP_SPEED 290
#define DOWN_SPEED 255
#define STOP_SPEED 0

// libraries
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
#include <String.h> 
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

// motor stats

int motor0Direction = 0;
int motor0Count = 2;
int motor0Switch = 0;
int motor0SwitchOld = 0; 


void setup() {
    pinMode(2, INPUT_PULLUP);
    
    // setup serial monitor
    Serial.begin(9600);
    
    // setup pwm shield
    pwm.begin();
    pwm.setPWMFreq(50);
    delay(100);
    for (int i=0; i<16; i++) {
      stopMotor(i);
    }
    delay(3000);
}

void loop() {   

  
  if (motor0Count == 0) {
    motor0Count = 2;
    upMotor(0);
    delay(10000);
    stopMotor(0);
  }
  
  if (motor0Switch == 0 && motor0SwitchOld == 1) {
    motor0Count = motor0Count -1;
  }
  Serial.println(motor0Count);
  motor0SwitchOld = motor0Switch;
  motor0Switch = digitalRead(2);
  delay(100);


}

void stopMotor(int motor_number) {
  pwm.setPWM(motor_number, 0, STOP_SPEED);
}

void upMotor(int motor_number) {
  pwm.setPWM(motor_number, 0, UP_SPEED);
}

void downMotor(int motor_number) {
  pwm.setPWM(motor_number, 0, DOWN_SPEED);
}
