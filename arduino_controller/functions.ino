//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

// This file contains functions that process the data that is received from the
// raspberry pi

//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

void ProcessData()
{
  while (go == true)
  {
    // initialize motors and get them moving
    for (int i = 0; i < NUMBER_MOTORS; i++)
    {
      CountMoving();
      if (moving_motors < NUMBER_MOTORS_MOVING && motor_commands[i][2] != 1)
      {
        if (motor_commands[i][1] != 0)
        {
          StartMotors(i);
          motor_commands[i][2] = 1;
        }
      }
    }

    // subtract from motor rotations when a rotation is detected
    for (int i = 0; i < NUMBER_MOTORS; i++)
    {
      if (motor_commands[i][2] == 1)
      {
        CheckCounter(i);
      }
    }
    // stop motors that have reached 0
    for (int i = 0; i < NUMBER_MOTORS; i++)
    {
      if (motor_commands[i][1] <= 0 && motor_commands[i][2] == 1)
      {
        my_servo[i].write(90);
        motor_commands[i][2] = 0;
      }
    }

    // stop motors that have hit the reset
    // first stop the motor and then tell the code to move it down one rotation
    for (int i = 0; i < NUMBER_MOTORS; i++)
    {
      if (digitalRead(ports[i][2]) == 0)
      {
        my_servo[i].write(90);
        motor_commands[i][0] = 1;
        motor_commands[i][1] = 1;
        motor_commands[i][2] = 0;
      }
    }

    // see how many turns are left in the array
    // we want to zero it every time we recalculate the number of turns
    total_turns = 0;
    for (int i = 0; i < NUMBER_MOTORS; i++)
    {
      total_turns += motor_commands[i][1];
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

//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

int CountMoving()
{
  moving_motors = 0;
  for (int i = 0; i < NUMBER_MOTORS; i++)
  {
    moving_motors += motor_commands[i][2];
  }
}

void CheckCounter(int i)
{
  motor_sensor_counter2[i] = motor_sensor_counter1[i];
  motor_sensor_counter1[i] = CheckSwitch(i, ports[i][1]);

  if (motor_sensor_counter1[i] == 1 && motor_sensor_counter2[i] == 0)
  {
    motor_commands[i][1] = motor_commands[i][1] - 1;
  }

  if (motor_commands[i][1] < 0)
  {
    motor_commands[i][1] = 0;
  }
}

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

void StartMotors(int i)
{
  if (motor_commands[i][0] == 0)
  {
    // Move up
    my_servo[i].write(80);
  }
  else if (motor_commands[i][0] == 1)
  {
    // Move down
    my_servo[i].write(100);
  }
  else if (motor_commands[i][0] == 2)
  {
    // Don't Move
    my_servo[i].write(90);
  }
  else if (motor_commands[i][0] == 3)
  {
    // Move Up for Reset
    my_servo[i].write(80);
  }
  else
  {
    // Don't Move
    my_servo[i].write(90);
  }
}
