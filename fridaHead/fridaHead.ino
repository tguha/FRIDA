#include <Servo.h>

Servo myservo;  // create servo object to control a servo
int receivedInt = -1;
int init_pos = 90;  // Initial position of the servo
int curr_pos = 90;  // Current position of the servo, initially set to init_pos
unsigned long lastMoveTime = 0;  // Timestamp of the last servo movement

void sweep() {
  moveServo(curr_pos, 0, 10);  // Move to one end at a speed of 60 degrees/second
  //curr_pos = 0;
  delay(100);
  moveServo(curr_pos, 180, 10);
  //curr_pos = 180;  // Update current position
}

void setup() {
  Serial.begin(115200);
  myservo.attach(9);  // attaches the servo on pin 9 to the servo object
  pinMode(LED_BUILTIN, OUTPUT);
  myservo.write(init_pos);// Move servo to initial position
  lastMoveTime = millis();  // Initialize lastMoveTime with the current time
  
}

void moveServo(int initial_pos, int final_pos, float speed) {
  bool face_found = false;
  // speed in degrees/second
  float time_step = 1000/speed;
  //time_step = 15;
  if (initial_pos < final_pos){
    for (int pos = initial_pos; pos <= final_pos; pos += 2) {
      face_found = checkFace();
      curr_pos += 2;
      if (face_found){
        return;
      }
      myservo.write(pos);              // Tell servo to go to position in variable 'pos'
      delay(int(time_step));                       // Waits 30ms for the servo to reach the position
    }
  }
  else{
    for (int pos = initial_pos; pos >= final_pos; pos -= 2) {
      face_found = checkFace();
      curr_pos -= 2;
      if (face_found){
        return;
      }
      myservo.write(pos);              // Tell servo to go to position in variable 'pos'
      delay(int(time_step));          // Waits 30ms for the servo to reach the position
    }
  }
}

bool checkFace(){
  if (Serial.available() > 0) {
    String receivedStr = Serial.readStringUntil('\n');
    Serial.println("OK");
    receivedInt = receivedStr.toInt();
    digitalWrite(LED_BUILTIN, LOW);
  }
  if (receivedInt == 0) {
    curr_pos += 1;
    lastMoveTime = millis();  // Reset the movement timer
    if (curr_pos > 180) {
      curr_pos = 180;
    }
    delay(13);
  }
  else if (receivedInt == 1) {
    curr_pos -= 1;
    lastMoveTime = millis();  // Reset the movement timer
    if (curr_pos < 0) {
      curr_pos = 0;
    }
    delay(13);
  }
    //lastMoveTime = millis();  // Reset the movement time
  else {
    //digitalWrite(LED_BUILTIN, HIGH);
  }
  myservo.write(curr_pos);  // Update the servo position
  // Check if the servo has been in the same position for more than 15 seconds
  return (receivedInt == 1 || receivedInt == 0);
}

void loop() {
  checkFace();
  while (millis() - lastMoveTime > 4000) {
    sweep();  // Reset position
    lastMoveTime = millis();  // Reset the movement timer
  }
 
}


