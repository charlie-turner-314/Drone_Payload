from gpiozero import AngularServo
from time import sleep
import logging

# Initialize the servo on GPIO pin 13
servo = AngularServo(13, min_angle=-90, max_angle=90, min_pulse_width=0.0006, max_pulse_width=0.0023)

def extend():
    global servo
    logging.info("Extending sampling tube")
    servo.angle = 90
    sleep(1)  # Adjust the sleep time as needed
    servo.detach()  # Detach the servo to stop it from holding the position
    logging.info("Sampling tube extended")

def retract():
    global servo
    logging.info("Retracting sampling tube")
    servo.angle = -90
    sleep(1)  # Adjust the sleep time as needed
    servo.detach()  # Detach the servo to stop it from holding the position
    logging.info("Sampling tube retracted")