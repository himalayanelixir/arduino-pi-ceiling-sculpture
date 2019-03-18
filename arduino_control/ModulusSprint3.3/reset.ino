void Reset1() {
  myservo1.write(100);
  while(true) {
    if(digitalRead(motor_reset_port) == 0){
      break;
    }
  }
}