void stopMotor(int motor_number) {
  pwm.setPWM(motor_number, 0, STOP_SPEED);
}

void upMotor(int motor_number) {
  pwm.setPWM(motor_number, 0, UP_SPEED);
}

void downMotor(int motor_number) {
  pwm.setPWM(motor_number, 0, DOWN_SPEED);
}
