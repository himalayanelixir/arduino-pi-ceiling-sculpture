//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

// This file contains functions that process the data that is received from the
// raspberry pi

//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

void ProcessData()
{
  // Added this because reset code is different from regular movement code
  bool is_reset = false;
  bool go = true;
  int total_turns = 0;
  long timeout_counter = 0;

  PopulateArray();

  // initialize all motors and get them moving
  for (int i = 0; i < NUMBER_MOTORS; i++)
  {
    if (motor_commands[i][0] == 0)
    {
      // Move up
      my_servo[i].write(80);
      is_reset = false;
    }
    else if (motor_commands[i][0] == 1)
    {
      // Move down
      my_servo[i].write(100);
      is_reset = false;
    }
    else if (motor_commands[i][0] == 2)
    {
      // Don't Move
      my_servo[i].write(90);
      is_reset = false;
    }
    else if (motor_commands[i][0] == 3)
    {
      // Move Up for Reset
      my_servo[i].write(80);
      is_reset = true;
    }
    else
    {
      // Sends Error Message
    }
  }

  if (is_reset == false)
  {
    while (go == true)
    {
      // subtract from motor rotations when a rotation is detected
      for (int i = 0; i < NUMBER_MOTORS; i++)
      {
        motor_sensor_counter2[i] = motor_sensor_counter1[i];
        motor_sensor_counter1[i] = CheckSwitch(i, ports[i][1]);

        if (motor_sensor_counter1[i] == 1 && motor_sensor_counter2[i] == 0)
        {
          motor_commands[i][1]--;
        }

        if (motor_commands[i][1] < 0)
        {
          motor_commands[i][1] = 0;
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
        // Serial.print("Total number of turns in array: ");
        // Serial.println(total_turns);
      }
      // print the total number of turns left for each motor
      for (int i = 0; i < NUMBER_MOTORS; i++)
      {
        Serial.print("Motor ");
        Serial.print(i);
        Serial.print(": ");
        Serial.print(motor_commands[i][1]);
        Serial.print(" --  ");
      }
      Serial.println("");

      // exit loop if there are no more motor rotations remaining
      if (total_turns <= 0)
      {
        go = false;
      }
      total_turns = 0;

      // time out loop if stall
      if (timeout_counter >= TIMEOUT)
      {
        go = false;
        for (int i = 0; i < NUMBER_MOTORS; i++)
        {
          my_servo[i].write(90);
          Serial.println("Timeout");
        }
      }
      timeout_counter = timeout_counter + 1;
      Serial.println(timeout_counter);
    }
  }
  else
  {
    int reset_counter[NUMBER_MOTORS] = {0};

    for (int i = 0; i < NUMBER_MOTORS; ++i)
    {
      reset_counter[i] = 1;
    }

    while (go == true)
    {
      // stop motors that have reached 0
      for (int i = 0; i < NUMBER_MOTORS; i++)
      {
        if (digitalRead(ports[i][2]) == 0)
        {
          my_servo[i].write(90);
          reset_counter[i] = 0;
        }
      }
      // see how many turns are left in the array
      for (int i = 0; i < NUMBER_MOTORS; i++)
      {
        total_turns += reset_counter[i];
      }

      Serial.print("Total Turns: ");
      Serial.println(total_turns);

      if (total_turns <= 0)
      {
        go = false;
      }
      total_turns = 0;

      if (timeout_counter >= TIMEOUT)
      {
        go = false;
        for (int i = 0; i < NUMBER_MOTORS; i++)
        {
          my_servo[i].write(90);
          Serial.println("Timeout");
        }
      }
      timeout_counter = timeout_counter + 1;
      Serial.println(timeout_counter);
    }
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
  String received_string = "";
  // give the string the value of the char array
  received_string = received_chars;

  // now lets populate the motor command array with values from the received
  // string
  for (int i = 0; i < NUMBER_MOTORS; i++)
  {

    // we break everything in to pairs of values
    int search1 = (i * 2);
    int search2 = ((i * 2) + 1);

    String value1 = getValue(received_string, ',', search1);
    String value2 = getValue(received_string, ',', search2);

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
  //for (int i = 0; i < NUMBER_MOTORS; i++)
  //{
  //  Serial.print("Motor Number: ");
  //  Serial.print(i);
  //  Serial.print(" - Direction: ");
  //  Serial.print(motor_commands[i][0]);
  //  Serial.print(" - Rotations: ");
  //  Serial.println(motor_commands[i][1]);
  //}
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
  else
  {
    if (integrator[motor_number] < MAXIMUM)
      integrator[motor_number]++;
  }

  /* Step 2: Update the output state based on the integrator.  Note that the
    output will only change states if the integrator has reached a limit,
    either 0 or MAXIMUM. */

  if (integrator[motor_number] == 0)
  {
    previous_value[motor_number] = 0;
    return (0);
  }
  else if (integrator[motor_number] >= MAXIMUM)
  {
    previous_value[motor_number] = 1;
    return (1);
  }
  else
  {
    return (previous_value[motor_number]);
  }
}
