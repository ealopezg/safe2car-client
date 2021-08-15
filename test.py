import serial
import pynmea2
 
port = "/dev/ttyACM0"
 
def parseGPS(message):
    while True:
        if message.find('GGA') > 0:
            msg = pynmea2.parse(message)
            print('%02f, %07.4f′' % (msg.latitude, msg.longitude))
            print("Timestamp: %s -- Lat: %s %s -- Lon: %s %s -- Altitude: %s %s -- Satellites: %s" % (msg.timestamp,msg.lat,msg.lat_dir,msg.lon,msg.lon_dir,msg.altitude,msg.altitude_units,msg.num_sats))
            if msg.num_sats > 0:
                return (msg.latitude, msg.longitude)
            

 
 
serialPort = serial.Serial(port, baudrate = 9600, timeout = 0.5)
while True:
    message = serialPort.readline()
    print(message.decode("utf-8"))
    #parseGPS(message.decode("utf-8"))