void setup() {

  pinMode(motor_counter_port,INPUT_PULLUP);
  pinMode(motor_reset_port,INPUT_PULLUP);
  myservo1.attach(motor_port);
  myservo1.write(90);

  pinMode(motor_counter_port2,INPUT_PULLUP);
  pinMode(motor_reset_port2,INPUT_PULLUP);
  myservo2.attach(motor_port2);
  myservo2.write(90);
  
  Serial.begin(9600);
  Serial.println("<Arduino is ready>");
  Serial.println(">");
}

void loop() {
  RecvWithStartEndMarkers();
  ShowNewData();
  Finished();
}

//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

void ShowNewData() {
  if (newData == true) {
    newData = false;
    Serial.println("<");
    Serial.print("Arduino: ");
    Serial.println(receivedChars);
    // From here we execute the commands that were send via the message
    ProcessData();
  }
}

//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

void Finished() {
    Serial.println(">");
}

//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

void RecvWithStartEndMarkers() {
  static boolean recvInProgress = false;
  static byte ndx = 0;
  char startMarker = '<';
  char endMarker = '>';
  char rc;

  while (Serial.available() > 0 && newData == false) {
    rc = Serial.read();

    if (recvInProgress == true) {
      if (rc != endMarker) {
        receivedChars[ndx] = rc;
        ndx++;
        if (ndx >= numChars) {
          ndx = numChars - 1;
        }
      }
      else {
        receivedChars[ndx] = '\0'; // terminate the string
        recvInProgress = false;
        ndx = 0;
        newData = true;
      }
    }

    else if (rc == startMarker) {
      recvInProgress = true;
    }
  }

}

//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////


String getValue(String data, char separator, int index)
{
    int found = 0;
    int strIndex[] = { 0, -1 };
    int maxIndex = data.length() - 1;

    for (int i = 0; i <= maxIndex && found <= index; i++) {
        if (data.charAt(i) == separator || i == maxIndex) {
            found++;
            strIndex[0] = strIndex[1] + 1;
            strIndex[1] = (i == maxIndex) ? i+1 : i;
        }
    }
    return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}
