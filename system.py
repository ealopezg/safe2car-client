import RPi.GPIO as GPIO
from gpiozero import MotionSensor,Buzzer
from command import Command
from picamera import PiCamera
from datetime import datetime
from io import BytesIO
import os
import time

class System:
    def __init__(self,config):
        self.config = config
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.config.SIM_POWER_PIN,GPIO.OUT)
        GPIO.setup(self.config.CAR_POWER_PIN,GPIO.OUT)
        self.buzzer = Buzzer(config.BUZZER_PORT)
        self.pir = []
        self.pir.append(MotionSensor(config.PIR1_PORT))
        self.pir.append(MotionSensor(config.PIR2_PORT))
        self.pir.append(MotionSensor(config.PIR3_PORT))
        self.system_on = False
        GPIO.setup(self.config.CAR_POWER_PIN, False)

    def status(self,system):
        return {
            'buzzer': self.buzzer.is_active,
            'system': self.system_on,
            'cut_off_power': GPIO.input(self.config.CAR_POWER_PIN)
        }
    

    
    def turnOff(self):
        GPIO.cleanup()

    def activateBuzzer(self):
        self.buzzer.beep(on_time=0.05,off_time=0.05)
    
    def deactivateBuzzer(self):
        self.buzzer.off()
    
    def checkSerialPorts(self):
        print("Checking serial ports..")
        return os.path.exists(self.config.GPS_PORT) and os.path.exists(self.config.SIM_PORT)
    
    def toggleSIM(self):
        GPIO.output(self.config.SIM_POWER_PIN, True)
        time.sleep(3)
        GPIO.output(self.config.SIM_POWER_PIN, False)
    
    def makeCall(self,number):
        port = serial.Serial(SIM_PORT, baudrate=9600, timeout=1)
        print("Initializing the modem...")
        port.write(b'ATE0\r')
        time.sleep(5)
        #rcv = port.readline()
        #print(rcv.decode())
        port.write(b'AT\r')
        time.sleep(5)
        #rcv = port.readline()
        #print(rcv.decode())
        port.write('ATD{};\r'.format(number).encode())
        print("Calling… to {}".format(number))
        time.sleep(5)
        #rcv = port.readline()
        #print(rcv.decode())
        port.flush()
        port.close()
    
    def activateCarPowerCutter(self):
        GPIO.output(self.config.CAR_POWER_PIN, True)

    def deactivateCarPowerCutter(self):
        GPIO.output(self.config.CAR_POWER_PIN, False)
    
    def takePicture(self,save=False):
        stream = BytesIO()
        camera = PiCamera()
        camera.start_preview()
        time.sleep(2)
        camera.capture(stream, 'jpeg')
        timestamp = datetime.timestamp(datetime.now())
        if save:
            file = open("image_{}.txt".format(timestamp),"wb")
            file.write(stream.getbuffer())
            file.close()
        photo = stream.getvalue()
        stream.close()
        camera.close()
        return photo

