import serial
import os, time


def makeCall(number):
    port = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=1)
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
