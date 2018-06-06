/*--------------------VenDuino v0.44---------------
Vending machine using FULL ROTATION servos. Rotary encoder is used to select item (replaces four buttons).
I/O           PIN#
ServoA        ~11
ServoB        ~10
ServoC         ~9
ServoD         ~6
LEDready       13
coinInsert     12
Encoder CLK   2
Encoder DT    3 
Encoder Switch  4
A0-A4 Nokia5110 LCD
(84x48 pixel screen) (x,y)

*/

#include <Servo.h> 

const int ServoA = 3;
const int clockwise = 1700;
const int counterclockwise = 1300;


const int LEDready = 13;
const int coinInsert = 12;

long previousMillis = 0;
long intervalIdle = 500;
int LEDreadyState = LOW;
int angle = 0;
long inputangle = 0;

void setup() { 
 pinMode(3, OUTPUT);
 pinMode(10, INPUT);
 Serial.begin(9600);
 Serial.println("--- Start Serial Monitor SEND_RCVE ---");
}
//_______________________MASTER LOOP__start____________________
void loop(){ 
  //inputangle = Serial.parseInt()   
  servoA();
  
  //angle = readPos(10);
  Serial.println(angle);
}

//_______________________MASTER LOOP_end_____________________

void servoA(){
   for(int i=0; i<2; i++){                  // change this to adjust +- full revolution
    digitalWrite(ServoA,HIGH);
    delayMicroseconds(clockwise); 
    digitalWrite(ServoA,LOW);
    delay(18); // 18.5ms 
    delayMicroseconds(300);
   }
  delay(1000);  

 }


int readPos(int pwmPin)
{
 int tHigh;
 int tLow;
 int tCycle;

 float theta = 0;
 float dc = 0;
 int unitsFC = 360;
 float dcMin = 0.029;
 float dcMax = 0.971;
 float dutyScale = 1;
 while(1) {
   pulseIn(pwmPin, LOW);
   tHigh = pulseIn(pwmPin, HIGH);
   tLow =  pulseIn(pwmPin, LOW);
   tCycle = tHigh + tLow;
   if ((tCycle > 1000) && ( tCycle < 1200)) break;
 }

 dc = (dutyScale * tHigh) / tCycle;
 theta = ((dc - dcMin) * unitsFC) / (dcMax - dcMin);
 return theta;
}




 
