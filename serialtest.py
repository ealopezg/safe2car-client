from serial import Serial

port = Serial("/dev/ttyS0", baudrate=9600, timeout=1)
while True:
    msg = port.readline()
    print(msg)