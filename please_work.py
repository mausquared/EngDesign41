from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import face_recognition
import imutils
import pickle
import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BOARD) #setup pins for correct gpio 
GPIO.setup(3,GPIO.OUT) #set pin 3 for output of PWM signal
pwm=GPIO.PWM(3,60) #set the rate for the PWM 
pwm.start(0) #start the PWM 

def SetAngle(angle):
    duty = angle / 18+2
    GPIO.output(3,True)
    pwm.ChangeDutyCycle(duty)
    sleep(1)
    GPIO.output(3, False)
    pwm.ChangeDutyCycle(0)

def OpenDoor(x):
    SetAngle(180) #rotates the servo anticlockwise
    SetAngle(180)
    SetAngle(180)
    pwm.stop()
    GPIO.cleanup()

def CloseDoor():
    SetAngle(50) #rotates the servo clockwise
    SetAngle(50)
    SetAngle(50)
    pwm.stop()
    GPIO.cleanup()

#from imutils.video import VideoStream

#import stuff for GPIO pins
# from gpiozero import AngularServo
# servo = AngularServo(18, initial_angle=0, min_pulse_width=?,max_pulse_width=?)

camera = PiCamera()
camera.resolution = (320,240)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(320,240))

currentname = "Unknown"
encodingsP = "encodings.pickle"
print("[INFO] loading encodings + face detector...")
data = pickle.loads(open(encodingsP, "rb").read())

time.sleep(0.1)

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    
    image = frame.array
    
    boxes = face_recognition.face_locations(image)
    encodings = face_recognition.face_encodings(image, boxes)
    names = []
    
    for encoding in encodings:
        matches = face_recognition.compare_faces(data["encodings"], encoding)
        name = "Unknown"
        
        if True in matches:
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}
            
            for i in matchedIdxs:
                name = data["names"][i]
                counts[name] = counts.get(name, 0) + 1
                
            name = max(counts, key=counts.get)
            
            if currentname != name:
                currentname = name
                print(currentname)
                
                ### hier wat er moet gebeuren bij een algemene hit
                ### dus bvb message zenden of signal zenden of etc.
                ### als goed is zou die vanaf hier dan activeren als gescand is
                
                ### dit hier onder is voor een servo, maar kan nu niet testen want geen servo
                
             if name == "Luc":
                OpenDoor()
                sleep(1)
                CloseDoor()
                
            
        
        names.append(name)
    
    for ((top, right, bottom, left), name) in zip(boxes, names):
        cv2.rectangle(image, (left, top), (right, bottom),(0, 255, 225), 2)
        y = top - 15 if top - 15 > 15 else top + 15
        cv2.putText(image, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,.8, (0, 255, 255), 2)
    
    cv2.imshow("Frame", image)
    key = cv2.waitKey(1) & 0xFF
    
    rawCapture.truncate(0)
    
    
    
    if key == ord("q"):
        break
    