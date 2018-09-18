void Reset1() {
  myservo1.write(100);
  while(true) {
    if(digitalRead(motor_reset_port) == 0){
      break;
    }
  }
}

void Reset2() {
  myservo2.write(100);
    while(true) {
    if(digitalRead(motor_reset_port2) == 0){
      break;
    }
  }
}
