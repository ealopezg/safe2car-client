
from config import Config
import pysher
from gpiozero import MotionSensor
from threading import *
import time
import queue
import json
from command import Command
import os
from testCamera import takePicture
import requests

from test4 import makeCall

config = Config('config.ini')

pir = MotionSensor(config.PIR1_PORT)

system_on = False
power_cut_off = True


pusher = pysher.Pusher(config.PUSHER_KEY,secure=False,custom_host=config.PUSHER,port=config.PUSHER_PORT,secret=config.PUSHER_SECRET)

api = requests.Session()
api.headers.update({"Authorization":"Bearer "+config.TOKEN,"Accept": "application/json"})
CHANNEL_ID = 'private-vehicle.'+str(config.VEHICLE_ID)

def pusher_connect_handler(data):
    data = json.loads(data)
    auth = register(data.get('socket_id'),CHANNEL_ID)
    channel = pusher.subscribe(CHANNEL_ID,auth=auth)
    channel.bind('action', receiveCommand)



def register(socket_id,channel):
    data = {
        'socket_id': socket_id,
        'channel_name': channel
        }
    r = api.post(config.BASE_URL+'/broadcasting/auth',data)
    return r.json()['auth']

def checkSerialPorts():
    print("Checking serial ports..")
    return os.path.exists(config.GPS_PORT) and os.path.exists(config.SIM_PORT)


def sendCommand(send_q,receive_q,pir_q,action_q):
    while True:
        command = send_q.get()
        if command:
            print(command)
            time.sleep(5)

def receiveCommand(send_q,receive_q,pir_q,action_q):
    while True:
        print("1. Tomar foto, 2. Obtener Ubicacion, 3. Hacer sonar alarma, 4. Corta corriente,5. Realizar llamada, 6. Encender/Apagar Sistema")
        option = int(input())
        if option == 1:
            action_q.put(Command('image',None))
        elif option == 2:
            action_q.put(Command('gps',None))
        elif option == 3:
            action_q.put(Command('alarm',None))
        elif option == 4:
            action_q.put(Command('power_cut_off',None))
        elif option == 5:
            action_q.put(Command('call',{'number':'951190956'}))
        elif option == 6:
            action_q.put(Command('system_toggle',None))
        

def pirLoop(send_q,receive_q,pir_q,action_q):
    global system_on
    while system_on:
        pir.wait_for_motion()
        send_q.put(Command.pirCommand())
        #action_q.put(Command('image',None))
        pir.wait_for_no_motion()
        
def actionLoop(send_q,receive_q,pir_q,action_q):
    global system_on
    while True:
        command = action_q.get()
        if command:
            if command.type == 'image':
                print("Taking picture...");
                send_q.put(Command.okCommand(command))
                response = takePicture(True)
                send_q.put(response)
            elif command.type == 'gps':
                print("Getting gps info...")
                send_q.put(Command.okCommand(command))
            elif command.type == 'alarm':
                print("Making the alarm sound...")
                send_q.put(Command.okCommand(command))
            elif command.type == 'power_cut_off':
                print("Cutting off the car...")
                send_q.put(Command.okCommand(command))
            elif command.type == 'call':
                print("Making a call...")
                send_q.put(Command.okCommand(command))
                makeCall(command.args['number'])
            elif command.type == 'system_toggle':
                print("Toggling the system...")
                system_on = not system_on
                send_q.put(Command.okCommand(command))
        time.sleep(5)
        

if __name__ == "__main__":
    checkSerialPorts()
    send_q = queue.Queue()
    receive_q = queue.Queue()
    pir_q = queue.Queue()
    action_q = queue.Queue()
    send_t = Thread(target=sendCommand, args=(send_q,receive_q,pir_q,action_q,))
    receive_t = Thread(target=receiveCommand, args=(send_q,receive_q,pir_q,action_q,))
    pir_t = Thread(target=pirLoop, args=(send_q,receive_q,pir_q,action_q,))
    action_t = Thread(target=actionLoop, args=(send_q,receive_q,pir_q,action_q,))
    send_t.start()
    receive_t.start()
    pir_t.start()
    action_t.start()

    send_t.join()
    receive_t.join()
    pir_t.join()
    action_t.join()

    pusher.connection.bind('pusher:connection_established', pusher_connect_handler)
    pusher.connect()
