int ledPin = 13;  // LED connected to digital pin 13
int inPin = 4;    // pushbutton connected to digital pin 7
int val = 0;      // variable to store the read value

void setup() {
  Serial.begin(9600);
  pinMode(inPin, INPUT_PULLUP);    // sets the digital pin 7 as input
}

void loop() {
  val = digitalRead(inPin);   // read the input pin
  Serial.println(val);
  delay(500);
}
