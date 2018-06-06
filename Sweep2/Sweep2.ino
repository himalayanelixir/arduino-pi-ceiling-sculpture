#include <Servo.h>

Servo myservo;
 
void setup() {
myservo.attach(9);
}
 
void loop() {
myservo.write(0);
delay(1000);
myservo.write(40);
delay(1000);
}
