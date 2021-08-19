import serial
import os, time


def makeCall(number):
    port = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=1)
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

def sendSMS(number,message):
    port = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=1)
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

def checkSIM():
    port = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=1)
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

print(checkSIM())
#makeCall('951190956')
#sendSMS('951190956','hola')