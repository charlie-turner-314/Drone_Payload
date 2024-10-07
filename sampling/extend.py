from gpiozero import AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

# Initialize the PiGPIOFactory
factory = PiGPIOFactory(host="127.0.0.1",port=60156)

# Create the servo object using the factory
servo = AngularServo(12, min_pulse_width=0.0006, max_pulse_width=0.0023, pin_factory=factory)

# Move the servo
servo.angle = 90
sleep(0.12)