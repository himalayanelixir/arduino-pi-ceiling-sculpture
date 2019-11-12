#include <Servo.h>

Servo myservo;  // create servo object to control a servo
Servo myservo2;
// twelve servo objects can be created on most boards

int pos = 0;    // variable to store the servo position

void setup() {
  pinMode(11, OUTPUT);
  pinMode(8, OUTPUT);
  digitalWrite(11, LOW);
  digitalWrite(8, LOW);
  myservo.attach(11);  // attaches the servo on pin 11 to the servo object
  myservo2.attach(8);
}

void loop() {
    myservo.write(80);
    myservo2.write(80);
    delay(60000);
    myservo.write(90);
    myservo2.write(90);
    delay(4000);
    myservo.write(100);
    myservo2.write(100);
    delay(60000);
    myservo.write(90);
    myservo2.write(90);
    delay(4000);
}
