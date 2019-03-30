//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

// This file contains funcitons that process the data that is recieved from the
// raspberry pi

//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

void ProcessData() {

  PopulateArray();
  
  /*   
  // Print First Number
  Serial.println("---------");
  Serial.print("Motor 1: ");
  Serial.println(motor_rotation_number);

  while (true) {

    motor_sensor_counter2 = motor_sensor_counter1;
    checkswitch(motor_counter_port);
    motor_sensor_counter1 = output;
    delay(10);

    if (motor_rotation_number == 0) {
      myservo1.write(90);
      break;
    }

    if (digitalRead(motor_reset_port) == 0) {
      myservo1.write(90);
      break;
    }

    if (motor_sensor_counter1 == 1 && motor_sensor_counter2 == 0) {
      motor_rotation_number--;

      // Print Number Every Time It Changes
      Serial.print("Motor 1: ");
      Serial.println(motor_rotation_number);
    }
  } */

  // Send Finished Signal
  Finished();
}

//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

void PopulateArray() {

  // 
  String recieved_string = "";
  recieved_string = received_chars;

  for (int i = 0; i < NUMBER_MOTORS; i++)
  {
    int search1 = (i * 2);
    int search2 = ((i * 2 ) + 1);
    
    String value1 = getValue(recieved_string, ',', search1);
    String value2  = getValue(recieved_string, ',', search2);
    
    if (value1 == "Up") {
      motor_commands[i][1] = 0;
    }
    else if (value1 == "Down") {
      motor_commands[i][1] = 1;
    }

    else if (value1 == "None") {
      motor_commands[i][1] = 2;
    }
    else if (value1 == "Reset") {
      motor_commands[i][1] = 3;
    }
    else
    {
      // Sends Error Message
      Invalid();
    }

    motor_commands[i][2] = value2.toInt();
  }

  // print array
  for (int i = 0; i < NUMBER_MOTORS; i++)
  {
    Serial.print("Motor Number: ");
    Serial.print(i);
    Serial.print(" - ");
    Serial.print(motor_commands[i][1]);
    Serial.print(" - ");
    Serial.println(motor_commands[i][2]);
  }


}

//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

void CheckSwitch(int switchPort) {
  // /* Step 1: Update the integrator based on the input signal.  Note that the
  //   integrator follows the input, decreasing or increasing towards the limits
  //   as determined by the input state (0 or 1). */
  // input = digitalRead(switchPort);

  // if (input == 0)
  // {
  //   if (integrator > 0)
  //     integrator--;
  // }
  // else if (integrator < MAXIMUM)
  //   integrator++;

  // /* Step 2: Update the output state based on the integrator.  Note that the
  //   output will only change states if the integrator has reached a limit,
  //   either 0 or MAXIMUM. */

  // if (integrator == 0)
  //   output = 0;
  // else if (integrator >= MAXIMUM)
  // {
  //   output = 1;
  //   integrator = MAXIMUM;  /* defensive code if integrator got corrupted */
  // }

  // /********************************************************* End of
  // debounce.c */
}

/* void Reset1() {
  myservo1.write(100);
  while(true) {
    if(digitalRead(motor_reset_port) == 0){
      break;
    }
  }
} */