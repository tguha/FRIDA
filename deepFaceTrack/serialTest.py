import serial
import time

# Replace '/dev/ttyACM0' with your Arduino's serial port
arduino = serial.Serial('/dev/cu.usbmodem11101', 9600)
time.sleep(2) # Wait for the connection to initialize

# Function to send an integer to the Arduino
def send_to_arduino(number):
    arduino.write(str(number).encode())
    time.sleep(0.3) # Short delay to ensure data is sent

# Example usage
try:
    send_to_arduino(1) # Turns the LED on
except:
    print("e")
time.sleep(2) # Wait for 2 seconds
try:
    send_to_arduino(0) # Turns the LED on
except:
    print("e")
time.sleep(2)
try:
    send_to_arduino(1) # Turns the LED on
except:
    print("e")
time.sleep(2) # Wait for 2 seconds
try:
    send_to_arduino(0) # Turns the LED on
except:
    print("e")

arduino.close() # Close the serial connection
