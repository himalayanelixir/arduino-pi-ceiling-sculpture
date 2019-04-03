//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

// This file contains funcitons that process the data that is recieved from the
// raspberry pi

//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

void ProcessData()
{

  PopulateArray();

  // initialize all motors and get them moving
  for (int i = 0; i < NUMBER_MOTORS; i++)
  {
    if (motor_commands[i][0] == 0)
    {
      my_servo[i].write(100);
    }
    else if (motor_commands[i][0] == 1)
    {
      my_servo[i].write(80);
    }
    else if (motor_commands[i][0] == 2)
    {
      my_servo[i].write(90);
    }
    else if (motor_commands[i][0] == 3)
    {
      // call reset function (still needs to be written)
    }
    else
    {
      // Sends Error Message
      Invalid();
    }
  }

  bool go = true;
  int total_turns = 0;

  while (go == true)
  {
    // subtract from motor rotations when a rotation is detected
    for (int i = 0; i < NUMBER_MOTORS; i++)
    {
      motor_sensor_counter2[i] = motor_sensor_counter1[i];
      motor_sensor_counter1[i] = CheckSwitch(i, ports[i][0]);

      if (motor_sensor_counter1[i] == 1 && motor_sensor_counter2[i] == 0)
      {
        motor_commands[i][1] = motor_commands[i][1] - 1;
      }
    }
    // stop motors that have reached 0
    for (int i = 0; i < NUMBER_MOTORS; i++)
    {
      if (motor_commands[i][1] <= 0)
      {
        my_servo[i].write(90);
      }
    }
    // see how many turns are left in the array
    for (int i = 0; i < NUMBER_MOTORS; i++)
    {
      total_turns += motor_commands[i][1];
    }
    // exit loop if there are no more motor rotations remaining
    if (total_turns <= 0)
    {
      go = false;
    }
    total_turns = 0;
  }
  // Send Finished Signal
  Finished();
}

//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

void PopulateArray()
{

  // temp string used to store the char array
  // easier to do opperations on string than chars
  String recieved_string = "";
  // give the string the value of the char array
  recieved_string = received_chars;

  // now lets populate the motor command array with values from the recieved
  // string
  for (int i = 0; i < NUMBER_MOTORS; i++)
  {
    int search1 = (i * 2);
    int search2 = ((i * 2) + 1);

    String value1 = getValue(recieved_string, ',', search1);
    String value2 = getValue(recieved_string, ',', search2);

    if (value1 == "Up")
    {
      motor_commands[i][0] = 0;
    }
    else if (value1 == "Down")
    {
      motor_commands[i][0] = 1;
    }
    else if (value1 == "None")
    {
      motor_commands[i][0] = 2;
    }
    else if (value1 == "Reset")
    {
      motor_commands[i][0] = 3;
    }
    else
    {
      // Sends Error Message
      Invalid();
    }

    motor_commands[i][1] = value2.toInt();
  }

  // print array
  for (int i = 0; i < NUMBER_MOTORS; i++)
  {
    Serial.print("Motor Number: ");
    Serial.print(i);
    Serial.print(" - ");
    Serial.print(motor_commands[i][0]);
    Serial.print(" - ");
    Serial.println(motor_commands[i][1]);
  }
}

//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

int CheckSwitch(int motor_number, int switchPort)
{
  /* Step 1: Update the integrator based on the input signal.  Note that the
    integrator follows the input, decreasing or increasing towards the limits
    as determined by the input state (0 or 1). */
  input[motor_number] = digitalRead(switchPort);

  if (input[motor_number] == 0)
  {
    if (integrator[motor_number] > 0)
      integrator[motor_number]--;
  }
  else if (integrator[motor_number] < MAXIMUM)
    integrator[motor_number]++;

  /* Step 2: Update the output state based on the integrator.  Note that the
    output will only change states if the integrator has reached a limit,
    either 0 or MAXIMUM. */

  if (integrator[motor_number] == 0)
    return (0);
  else if (integrator[motor_number] >= MAXIMUM)
  {
    return (1);
    integrator[motor_number] = MAXIMUM; /* defensive code if integrator got corrupted */
  }
}