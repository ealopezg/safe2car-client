import RPi.GPIO as GPIO
from gpiozero import MotionSensor,Buzzer
from command import Command
from picamera import PiCamera
from datetime import datetime
from io import BytesIO
import os
import time
import serial
import subprocess

import io

import pynmea2

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
    
    def checkLanCable():
        cmd = subprocess.run(['cat', '/sys/class/net/eth0/operstate'], stdout=subprocess.PIPE)
        if cmd.returncode == 0:
            return cmd.stdout.decode().strip() == 'up'
        else:
            return False


    
    def turnOff(self):
        GPIO.cleanup()

    def activateBuzzer(self):
        self.buzzer.beep(on_time=0.05,off_time=0.05)
    
    def deactivateBuzzer(self):
        self.buzzer.off()
    
    def powerOnSIM(self):
        GPIO.output(self.config.SIM_POWER_PIN, True)
        time.sleep(3)
        GPIO.output(self.config.SIM_POWER_PIN, False)

    def checkSIM(self):
        if os.path.exists(self.config.SIM_PORT):
            port = serial.Serial(self.config.SIM_PORT, baudrate=9600, timeout=1)
            try:
                port.write(b'ATE0\r\n')
                rcv = port.readline()
                port.write(b'AT\r\n')
                rcv = port.readline()
                response = rcv.decode().strip()
                port.flush()
            finally:
                port.close()
            return response == 'OK'
        return False
    

    def checkSerialPorts(self):
        print("Checking serial ports..")
        return os.path.exists(self.config.GPS_PORT) and os.path.exists(self.config.SIM_PORT)
    
    def toggleSIM(self):
        GPIO.output(self.config.SIM_POWER_PIN, True)
        time.sleep(3)
        GPIO.output(self.config.SIM_POWER_PIN, False)
    
    def makeCall(self,number):
        port = serial.Serial(self.config.SIM_PORT, baudrate=9600, timeout=1)
        try:
            port.flush()
            time.sleep(2)
            print("MODEM: Initializing the modem...")
            port.write(b'ATZ\r\n')
            time.sleep(2)
            rcv = port.readline()
            print('MODEM: '+rcv.decode().strip())
            port.write(b'ATE0\r\n')
            time.sleep(2)
            rcv = port.readline()
            print('MODEM: '+rcv.decode().strip())
            port.write(b'AT\r\n')
            time.sleep(2)
            rcv = port.readline()
            print('MODEM: '+rcv.decode().strip())
            print("MODEM: Calling to {}".format(number))
            port.write('ATD{};\r\n'.format(number).encode())
            time.sleep(2)
            rcv = port.readline()
            print('MODEM: '+rcv.decode().strip())
            port.flush()
        finally:
            port.close()
    
    
    def sendSMS(self,number,message):
        port = serial.Serial(self.config.SIM_PORT, baudrate=9600, timeout=1)
        try:
            port.flush()
            time.sleep(2)
            print("MODEM: Initializing the modem...")
            port.write(b'ATZ\r\n')
            time.sleep(2)
            rcv = port.readline()
            print('MODEM: '+rcv.decode().strip())
            port.write(b'ATE0\r\n')
            time.sleep(2)
            rcv = port.readline()
            print('MODEM: '+rcv.decode().strip())
            port.write(b'AT\r\n')
            time.sleep(2)
            rcv = port.readline()
            print('MODEM: '+rcv.decode().strip())
            print("MODEM: Sending sms to {}".format(number))
            port.write(b'AT+CMGF=1\r\n')
            time.sleep(2)
            rcv = port.readline()
            print('MODEM: '+rcv.decode().strip())
            port.write(b'AT+CMGS="' + number.encode() + b'"\r\n')
            time.sleep(2)
            rcv = port.readline()
            print('MODEM: '+rcv.decode().strip())
            port.write(message.encode())
            time.sleep(2)
            rcv = port.readline()
            print('MODEM: '+rcv.decode().strip())
            port.write(bytes([26]))
            time.sleep(2)
            rcv = port.readline()
            print('MODEM: '+rcv.decode().strip())
            port.flush()
        finally:
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
            file = open("image_{}.jpg".format(timestamp),"wb")
            file.write(stream.getbuffer())
            file.close()
        photo = stream.getvalue()
        stream.close()
        camera.close()
        return photo
    
    def getLocation(self):
        ser = serial.Serial(self.config.GPS_PORT, 9600, timeout=1)
        ser.flush()
        sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
        loc = None
        timeout = time.time() + 20
        while True:
            try:
                line = sio.readline()
                if line.find('GGA') > 0:
                    msg = pynmea2.parse(line)
                    loc = (msg.latitude, msg.longitude)
                    break
                if time.time() > timeout:
                    break
            except serial.SerialException as e:
                print('Device error: {}'.format(e))
                break
            except pynmea2.ParseError as e:
                print('Parse error: {}'.format(e))
                continue

        ser.flush()
        ser.close()
        return loc

