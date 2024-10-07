from gpiozero import AngularServo
from time import sleep
from gpiozero.pins.pigpio import PiGPIOFactory

def extend():
    print("Extending")
    servo = AngularServo(12, min_pulse_width = 0.0006, max_pulse_width = 0.0023)
    servo.angle = 90
    sleep(0.12)

def retract():
    servo = AngularServo(12, min_pulse_width = 0.0006, max_pulse_width = 0.0023)

    servo.angle = -90
    sleep(0.12)