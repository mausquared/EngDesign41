from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import face_recognition
import imutils
import pickle
import RPi.GPIO as GPIO
from time import sleep
from gpiozero import Button
import pygame
import random
from num2words import num2words
from subprocess import call

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

def OpenDoor():
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
    
def button_press(): #function for button press
    pygame.mixer.init() # initializes mixer module of pygame
    pygame.mixer.music.load(random.choice(music_list)) # load the music file to the mixer
    while pygame.mixer.music.get_busy() == True:
        continue     
    print("Button pressed")
    pygame.mixer.music.play()
    
def TTS(name):
    
    cmd_beg= 'espeak '
    cmd_end= ' | aplay /home/pi/Desktop/Text.wav  2>/dev/null' # To play back the stored .wav file and to dump the std errors to /dev/null
    cmd_out= '--stdout > /home/pi/Desktop/Text.wav ' # To store the voice file    espeak.set_parameter(espeak.Paameter.rate,100)
    
    text = name 
    #print(text)
    #Replacing ' ' with '_' to identify words in the text entered
    text = text.replace(' ', '_')

    #Calls the Espeak TTS Engine to read aloud a Text
    call([cmd_beg+cmd_out+text+cmd_end], shell=True)

    print("script finished")
    
    #calling this function should be done in this manner:
    #TTS(name)
    #sleep(0.5)
    #TTS("Is at the door")


music_list = ['doorbell-1.mp3']
button = Button(18)
# while(True):
#     button.when_pressed = button_press

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
    
    button.when_pressed = button_press
    
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
                TTS(name)
                sleep(.5)
                TTS("Is at your front door")
                
            else:
                TTS("Uknown person")
                sleep(.5)
                TTS("At the front door")
                
                ### hier wat er moet gebeuren bij een algemene hit
                ### dus bvb message zenden of signal zenden of etc.
                ### als goed is zou die vanaf hier dan activeren als gescand is
                
                ### dit hier onder is voor een servo, maar kan nu niet testen want geen servo
                
#              if name == "Luc":
#                 OpenDoor()
#                 sleep(1)
#                 CloseDoor()
        
                
            
        
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
    
