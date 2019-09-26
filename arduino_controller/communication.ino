//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

// This file contains functions that help the arduino communitate with the
// raspberry pi

//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

// handles the receiving of data over the serial port
void RecvWithStartEndMarkers()
{
  static boolean recvInProgress = false;
  static byte ndx = 0;
  char startMarker = '<';
  char endMarker = '>';
  char rc;

  while (Serial.available() > 0 && new_data == false)
  {
    rc = Serial.read();

    if (recvInProgress == true)
    {
      if (rc != endMarker)
      {
        received_chars[ndx] = rc;
        ndx++;
        if (ndx >= num_chars)
        {
          ndx = num_chars - 1;
        }
      }
      else
      {
        received_chars[ndx] = '\0'; // terminate the string
        recvInProgress = false;
        ndx = 0;
        new_data = true;
      }
    }

    else if (rc == startMarker)
    {
      recvInProgress = true;
    }
  }
}

// helps get a particular value from the incoming data string
String getValue(String data, char separator, int index)
{
  int found = 0;
  int strIndex[] = {0, -1};
  int maxIndex = data.length() - 1;

  for (int i = 0; i <= maxIndex && found <= index; i++)
  {
    if (data.charAt(i) == separator || i == maxIndex)
    {
      found++;
      strIndex[0] = strIndex[1] + 1;
      strIndex[1] = (i == maxIndex) ? i + 1 : i;
    }
  }
  return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}

// sends message back to raspberry pi saying the command has been executed
void Finished()
{
  Serial.println("Finished Current Job!");
  Serial.println(">");
}

// sends error message back to raspberry pi
void Invalid()
{
  Serial.println("<");
  Serial.print("Arduino: ");
  Serial.println("Invalid Input!");
  Serial.println(">");
}
