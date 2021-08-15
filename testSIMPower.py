import RPi.GPIO as GPIO
import time

sim_power_pin = 24
GPIO.setmode(GPIO.BCM)
GPIO.setup(sim_power_pin,GPIO.OUT)

GPIO.output(sim_power_pin, True)
time.sleep(3)
GPIO.output(sim_power_pin, False)