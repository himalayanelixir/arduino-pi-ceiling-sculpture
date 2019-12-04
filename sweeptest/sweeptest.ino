#include <Servo.h>

Servo myservo;  // create servo object to control a servo
Servo myservo2;
// twelve servo objects can be created on most boards

int pos = 0;    // variable to store the servo position

void setup() {
  pinMode(2, OUTPUT);
  pinMode(3, INPUT_PULLUP);
  pinMode(8, OUTPUT);
  pinMode(34, OUTPUT);

  
  digitalWrite(2, LOW);
  digitalWrite(8, LOW);
  myservo.attach(2);  // attaches the servo on pin 11 to the servo object
  myservo2.attach(8);
}

void loop() {
    myservo.write(80);
    myservo2.write(80);
    for(int i = 0; i < 300; i++) {
      if (digitalRead(3) ==1) {
        digitalWrite(34, HIGH);
      }
      else {
        digitalWrite(34, LOW);
      }
      delay(100);
    }
    myservo.write(90);
    myservo2.write(90);
    for(int i = 0; i < 30; i++) {
      if (digitalRead(3) ==1) {
        digitalWrite(34, HIGH);
      }
      else {
        digitalWrite(34, LOW);
      }
      delay(100);
    }
    myservo.write(100);
    myservo2.write(100);
    for(int i = 0; i < 300; i++) {
      if (digitalRead(3) ==1) {
        digitalWrite(34, HIGH);
      }
      else {
        digitalWrite(34, LOW);
      }
      delay(100);
    }
    myservo.write(90);
    myservo2.write(90);
    for(int i = 0; i < 30; i++) {
      if (digitalRead(3) ==1) {
        digitalWrite(34, HIGH);
      }
      else {
        digitalWrite(34, LOW);
      }
      delay(100);
    }
}
