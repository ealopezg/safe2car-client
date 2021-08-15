import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(4, GPIO.IN)
time.sleep(10)

while True:
    print(GPIO.input(4))
    time.sleep(1)