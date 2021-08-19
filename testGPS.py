import io

import pynmea2
import serial
import time


# ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=5.0)
# sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))

# while 1:
#     try:
#         line = sio.readline()
#         if line.find('GGA') > 0:
#             msg = pynmea2.parse(line)
#             print('%02f, %07.4f′' % (msg.latitude, msg.longitude))
#             print("NUEVA LINEA")
#     except serial.SerialException as e:
#         print('Device error: {}'.format(e))
#         break
#     except pynmea2.ParseError as e:
#         print('Parse error: {}'.format(e))
#         continue


def getLocation():
    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=5.0)
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

    return loc

print(getLocation())
