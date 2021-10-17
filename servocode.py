import RPi.GPIO as GPIO
from time import sleep
GPIO.setmode(GPIO.BOARD)

GPIO.setup(3,GPIO.OUT)
pwm=GPIO.PWM(3,60)
pwm.start(0)

def SetAngle(angle):
    duty = angle / 18+2
    GPIO.output(3,True)
    pwm.ChangeDutyCycle(duty)
    sleep(1)
    GPIO.output(3, False)
    pwm.ChangeDutyCycle(0)
    
def OpenDoor():
    SetAngle(180)
    SetAngle(180)
    SetAngle(180)

def CloseDoor():
    SetAngle(50)
    SetAngle(50)
    SetAngle(50)

OpenDoor()
sleep(2)
CloseDoor()
print("Spinning of servo has finished")

pwm.stop()
GPIO.cleanup()