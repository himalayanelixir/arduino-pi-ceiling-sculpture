void stopMotor(int motor_number) {
  pwm.setPWM(motor_number, 0, 0);
}

void upMotor(int motor_number) {
  pwm.setPWM(motor_number, 0, 295);
}

void downMotor(int motor_number) {
  pwm.setPWM(motor_number, 0, 270);
}
