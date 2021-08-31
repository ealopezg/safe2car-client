import RPi.GPIO as GPIO
from gpiozero import MotionSensor,Buzzer,Button
from command import Command
from picamera import PiCamera
from datetime import datetime
from io import BytesIO
import os
import time
import serial
import subprocess
import sys
import io

import pynmea2

sb_was_held = False




    

class System:
    """System Class
    Used to control the system i/o
    it configures and controls the gpio pins
    and camera,gps and sim devices 
    """
    def __init__(self,config):
        self.config = config
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.config.SIM_POWER_PIN,GPIO.OUT)
        GPIO.setup(self.config.CAR_POWER_PIN,GPIO.OUT)
        self.buzzer = Buzzer(config.BUZZER_PORT)
        self.pir = []
        self.pir.append(MotionSensor(config.PIR1_PORT,queue_len=20))
        self.pir.append(MotionSensor(config.PIR2_PORT,queue_len=20))
        self.pir.append(MotionSensor(config.PIR3_PORT,queue_len=20))
        self.system_on = False
        self.shutdown_button = Button(self.config.SHUTDOWN_PIN)
        self.shutdown_button.when_released = self.restart
        self.shutdown_button.hold_time = 5
        self.shutdown_button.when_held = self.shutdown
        GPIO.setup(self.config.CAR_POWER_PIN, False)

        self._sim_using = False

    def status(self,system):
        """Generates a dict with actual config status of the system

        Args:
            system (bool): Describes if the system is activated or not

        Returns:
            dict
        """
        return {
            'buzzer': self.buzzer.is_active,
            'system': system,
            'cut_off_power': GPIO.input(self.config.CAR_POWER_PIN)
        }
    
    def checkInterface(self,interface):
        cmd = subprocess.run(['cat', '/sys/class/net/'+interface+'/operstate'], stdout=subprocess.PIPE)
        if cmd.returncode == 0:
            return cmd.stdout.decode().strip() == 'up'
        else:
            return False
    
    def restart(self):
        """Used to restart the device when the button is released and not helded
        """
        global sb_was_held
        if not sb_was_held:
            print("RESTART")
            self.toggleSIM() # Turns off the SIM808
            subprocess.run(["sudo","reboot"]) # Sends reboot command to the OS
        sb_was_held = False
    
    

    
    def shutdown(self):
        """Used to device when the button is pressed
        """
        global sb_was_held
        print("SHUTDOWN SYSTEM")
        self.toggleSIM() # Turns off the SIM808
        subprocess.run(["sudo","poweroff"]) # Sends poweroff command to the OS
        sb_was_held = True
    

    def activateBuzzer(self):
        self.buzzer.beep(on_time=0.05,off_time=0.05)
    
    def deactivateBuzzer(self):
        self.buzzer.off()
    

    def checkSIM(self):
        """Used to check if the SIM808 is connected and working,
        it sends AT commands waiting for an OK

        Returns:
            boolean: True if the SIM808 is connected and working, otherwise returns False
        """
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
        """Sends various AT commands to the SIM808 to make a call to the number

        Args:
            number (String): Phone number to make a call
        """
        while self._sim_using:
            time.sleep(1)
        self._sim_using = True
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
        self._sim_using = False
    
    def sendSMS(self,number,message):
        """Sends various AT commands to the SIM808 to send an SMS to the number

        Args:
            number (String): Phone number to make a call
            message (String): Message to send
        """
        while self._sim_using:
            time.sleep(1)
        self._sim_using = True
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
        self._sim_using = False


    def activateCarPowerCutter(self):
        GPIO.output(self.config.CAR_POWER_PIN, True)

    def deactivateCarPowerCutter(self):
        GPIO.output(self.config.CAR_POWER_PIN, False)
    
    def takePicture(self,save=False):
        """Takes a picture using the camera, it can save in the storage of the device as jpg

        Args:
            save (bool, optional): Boolean to save the image file or not. Defaults to False.

        Returns:
            bytes: Photo content
        """
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
        """Uses the gps device to return the coordinates

        Returns:
            tuple: GPS coordinates
        """
        ser = serial.Serial(self.config.GPS_PORT, 9600, timeout=1)
        
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

