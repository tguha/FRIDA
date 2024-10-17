#include <Servo.h>

Servo myservo;  // create servo object to control a servo
int receivedInt = 1;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  myservo.attach(8);

}

void loop() {
  //myservo.write(1560);

  
    myservo.write(1400);
    delay(1500); //down
     myservo.write(1560);
    delay(1600);
    myservo.write(1400);
    delay(1500); //down
    myservo.write(1560);
    delay(1600);
  

}
