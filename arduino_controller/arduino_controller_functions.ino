//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

void ProcessData() {

/*   // variables
  String recievedString = "";
  String motor_rotation_string = "";
  String motor_rotation_string2 = "";

  recievedString = receivedChars;

  // logic
  motor_direction = getValue(recievedString, ',', 0);
  motor_rotation_string = getValue(recievedString, ',', 1);
  motor_rotation_number = motor_rotation_string.toInt();

  //
  if (motor_direction == "Up") {
    myservo1.write(100);
  }
  else if (motor_direction == "Down") {
    myservo1.write(80);
  }

  else if (motor_direction == "None") {
    myservo1.write(90);
  }
  else if (motor_direction == "Reset") {
    Reset1();
  }
  else
  {
    // Sends Error Message
    Invalid();
  }

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

void checkswitch(int switchPort) {
  // /* Step 1: Update the integrator based on the input signal.  Note that the
  //   integrator follows the input, decreasing or increasing towards the limits as
  //   determined by the input state (0 or 1). */
  // input = digitalRead(switchPort);

  // if (input == 0)
  // {
  //   if (integrator > 0)
  //     integrator--;
  // }
  // else if (integrator < MAXIMUM)
  //   integrator++;

  // /* Step 2: Update the output state based on the integrator.  Note that the
  //   output will only change states if the integrator has reached a limit, either
  //   0 or MAXIMUM. */

  // if (integrator == 0)
  //   output = 0;
  // else if (integrator >= MAXIMUM)
  // {
  //   output = 1;
  //   integrator = MAXIMUM;  /* defensive code if integrator got corrupted */
  // }

  // /********************************************************* End of debounce.c */
}





/* void Reset1() {
  myservo1.write(100);
  while(true) {
    if(digitalRead(motor_reset_port) == 0){
      break;
    }
  }
} */