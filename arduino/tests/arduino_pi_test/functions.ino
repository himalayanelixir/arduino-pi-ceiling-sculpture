//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

// This file contains functions that process the data that is received from the
// raspberry pi

//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

// function that moves the motors and executes till they are done moving or timeout
void ProcessData()
{
    while (go == true)
    {
        // delay(5000);
        // go = false;
        digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)
        delay(50);                       // wait for a second
        digitalWrite(LED_BUILTIN, LOW);    // turn the LED off by making the voltage LOW
        delay(50);


        timeout_counter = timeout_counter + 1;

        // time out loop if stall
        if (timeout_counter >= TIMEOUT)
        {
            go = false;
            did_timeout = true;
            for (int i = 0; i < NUMBER_OF_MOTORS; i++)
            {
            my_servo[i].write(90);
            }
        }
    }
}

// count the number of moving motors
int CountMoving()
{
    moving_motors = 0;
    for (int i = 0; i < NUMBER_OF_MOTORS; i++) {
        moving_motors += motor_commands[i][2];
    }
}

// check to see if we are on a rising edge
void CheckCounter(int i)
{
    motor_sensor_counter2[i] = motor_sensor_counter1[i];
    motor_sensor_counter1[i] = CheckSwitch(i, ports[i][1]);

    if (motor_commands[i][0] == 1) {
        if (motor_sensor_counter1[i] == 1 && motor_sensor_counter2[i] == 0) {
            if (motor_commands[i][3] == 0) {
                motor_commands[i][1] = motor_commands[i][1] - 1;
            }
        }
    }
    else {
        if (motor_sensor_counter1[i] == 0 && motor_sensor_counter2[i] == 1) {
            if (motor_commands[i][3] == 0) {
                motor_commands[i][1] = motor_commands[i][1] - 1;
            }
        }
    }

    if (motor_commands[i][1] < 0) {
        motor_commands[i][1] = 0;
    }
}

// check to see if the encoder switch is pressed or not
int CheckSwitch(int motor_number, int switchPort)
{
    /* Step 1: Update the integrator based on the input signal.  Note that the
    integrator follows the input, decreasing or increasing towards the limits
    as determined by the input state (0 or 1). */
    input[motor_number] = digitalRead(switchPort);

    if (input[motor_number] == 0) {
        if (integrator[motor_number] > 0)
            integrator[motor_number]--;
    }
    else {
        if (integrator[motor_number] < MAXIMUM)
            integrator[motor_number]++;
    }

    /* Step 2: Update the output state based on the integrator.  Note that the
    output will only change states if the integrator has reached a limit,
    either 0 or MAXIMUM. */

    if (integrator[motor_number] == 0) {
        previous_value[motor_number] = 0;
        return (0);
    }
    else if (integrator[motor_number] >= MAXIMUM) {
        previous_value[motor_number] = 1;
        return (1);
    }
    else {
        return (previous_value[motor_number]);
    }
}

// move motors
void StartMotors(int i)
{
    if (motor_commands[i][0] == 1) {
        // Move up
        my_servo[i].write(80);
    }
    else if (motor_commands[i][0] == 2) {
        // Move down
        my_servo[i].write(110);
    }
    else if (motor_commands[i][0] == 0) {
        // Don't Move
        my_servo[i].write(90);
    }
    else if (motor_commands[i][0] == 3) {
        // Move Up for Reset
        my_servo[i].write(80);
    }
    else {
        // Don't Move
        my_servo[i].write(90);
    }
}
