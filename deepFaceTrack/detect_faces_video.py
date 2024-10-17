from imutils.video import VideoStream
import numpy as np
import argparse
import imutils
import time
import cv2

import subprocess
import serial

port = '/dev/cu.usbmodem14214201'
baud = 115200
arduino = serial.Serial(port, baud)
time.sleep(2) # Wait for the connection to initialize

# Function to send an integer to the Arduino
def send_to_arduino(arduino, number: int):
	try:
		arduino.write((str(number) + "\n").encode())  
		while True:
			if arduino.readline().decode().strip() == "OK":
				break  # Exit loop once "OK" is received'
		
	
	except Exception as e:
		print(e)  # Print the error if any
		arduino.close()
		try:
			# Find processes using the port
			lsof_output = subprocess.check_output(['lsof', port]).decode()
			for line in lsof_output.splitlines()[1:]:  # Skip the first line (headers)
				fields = line.split()
				pid = fields[1]
				subprocess.run(['kill', pid])  # Send SIGTERM to each process
		except subprocess.CalledProcessError:
			print(f"No process is currently using {port}.")

		time.sleep(2)
		for i in range(1):
			try:
				arduino = serial.Serial(port, baud, timeout=1)
				arduino.setDTR(False)  # Toggle DTR to reset Arduino
				time.sleep(1)
				arduino.flushInput()  # Flush startup text
				arduino.setDTR(True)
				time.sleep(2)
			except Exception as e1:
				print(e1)

		return arduino 
	return arduino
		

try:
	arduino = send_to_arduino(arduino, 1) # Turns the LED on
except:
	
	print("e")
time.sleep(1) # Wait for 2 seconds
try:
	arduino = send_to_arduino(arduino, 0) # Turns the LED on
except:
	print("e")
time.sleep(1)
try:
	arduino = send_to_arduino(arduino, 1) # Turns the LED on
except:
	print("e")
time.sleep(1) # Wait for 2 seconds
try:
	arduino = send_to_arduino(arduino , 0) # Turns the LED on
except:
	print("e")
time.sleep(1)
try:
	arduino = send_to_arduino(arduino, 1) # Turns the LED on
except:
	print("e")
time.sleep(1) # Wait for 2 seconds
try:
	arduino = send_to_arduino(arduino, 0) # Turns the LED on
except:
	print("e")
	
def getCenter(start_x, start_y, end_x, end_y):
	x = abs(start_x + end_x)/2
	y = abs(start_y + end_y)/2
	return x, y

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", required=True,
	help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", required=True,
	help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.5,
	help="minimum probability to filter weak detections")
args = vars(ap.parse_args())

# load our serialized model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

# initialize the video stream and allow the camera sensor to warmup
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
time.sleep(2.0)
iter = 0
send_pos = 0
new_send_pos = 0

# Define tuning parameters
K = 100  # Maximum speed in degrees per second
B = 0.1  # Decay rate
window_size = 20  # Center window size

def calculate_velocity(dist_from_center) -> float:
    if dist_from_center < window_size:
        return 0
    else:
        return K - K * np.exp(-B * dist_from_center)

# loop over the frames from the video stream
while True:
    # grab the frame from the threaded video stream and resize it
    # to have a maximum width of 400 pixels
    frame = vs.read()
    frame = imutils.resize(frame, width=400)
    frame = cv2.flip(frame, 0)
    # grab the frame dimensions and convert it to a blob
    (h, w) = frame.shape[:2]
    center_x = w / 2
    center_y = h / 2
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
        (300, 300), (104.0, 177.0, 123.0))

    # pass the blob through the network and obtain the detections and
    # predictions
    net.setInput(blob)
    detections = net.forward()
    iter += 1
    # loop over the detections
    face_x = 0
    face_y = 0

    num_faces = detections.shape[2]
    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        # filter out weak detections by ensuring the `confidence` is
        # greater than the minimum confidence
        if confidence < args["confidence"]:
            num_faces -= 1
            continue

        # compute the (x, y)-coordinates of the bounding box for the
        # object
        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
        (startX, startY, endX, endY) = box.astype("int")
        new_face_x, new_face_y = getCenter(startX, startY, endX, endY)
        face_x += new_face_x
        face_y += new_face_y
        

        # draw the bounding box of the face along with the associated
        # probability
        text = "{:.2f}%".format(confidence * 100)
        y = startY - 10 if startY - 10 > 10 else startY + 10
        cv2.rectangle(frame, (startX, startY), (endX, endY),
            (0, 0, 255), 2)
        cv2.putText(frame, text, (startX, y),
            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
    if num_faces != 0:
        face_x = face_x / num_faces
        face_y = face_y / num_faces
        dist_from_center = abs(face_x - 150)  # Calculate distance from center

        if face_x - 150 > window_size: # If face on left
            v = int(calculate_velocity(dist_from_center))
            print(f"\rMoving left with speed: {v} deg/sec", end='', flush=True)
            send_to_arduino(arduino, v)  #TODO! Can send_to_arduino function handle float values for velocity?? No
        elif face_x - 150 < -window_size:
            v = calculate_velocity(dist_from_center) # If face on right 
            print(f"\rMoving right with speed: {v} deg/sec", end='', flush=True)
            send_to_arduino(arduino, -v)  # NEG velocity to move right
        else:
            print("\rIn the center window", end='', flush=True)
            send_to_arduino(arduino, 0)
    else:
        print("\rNo face detected", end='', flush=True)
        send_to_arduino(arduino, 0)
    # show the output frame
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
arduino.close()

