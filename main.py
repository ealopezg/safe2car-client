
from config import Config
from system import System
import pysher
from gpiozero import MotionSensor,Buzzer
from threading import *
import time
import queue
import json
from command import Command
import os
from testCamera import takePicture
import requests
import pickle

config = Config('config.ini')
system = System(config)



system_on = False
power_cut_off = False

pusher = pysher.Pusher(config.PUSHER_KEY,secure=False,custom_host=config.PUSHER,port=config.PUSHER_PORT,secret=config.PUSHER_SECRET)

api = requests.Session()
api.headers.update({"Authorization":"Bearer "+config.TOKEN,"Accept": "application/json"})
CHANNEL_ID = 'private-vehicle.'+str(config.VEHICLE_ID)

def motionDetected():
    global system_on
    if system_on:
        send_q.put(Command.pirCommand())

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
    print(r.json())
    return r.json()['auth']


def sendCommand():
    while True:
        command = send_q.get()
        if command:
            print(command.toObject())
            r = api.post(config.BASE_URL+'/api/vehicle/action',json=command.toObject())
            print(r.text)
            print('Command Sended: action:{} status: {}'.format(command.action,r.status_code))


def receiveCommand(data):
    data = json.loads(data).get('status')
    if data:
        command = Command.fromJson(data)
        action_q.put(command)



        
def actionLoop():
    global system_on
    while True:
        command = action_q.get()
        if command:
            print(command)
            if command.action == 'photo':
                print("Taking picture...");
                send_q.put(command.ok())
                photo = system.takePicture(True)
                send_q.put(command.photo(photo))
            elif command.action == 'location':
                print("Getting gps info...")
                send_q.put(command.ok())
                send_q.put(command.gps(52.6206345, -2.1601284))
            elif command.action == 'power_cut_off_activate':
                print("Enabling Power cut...")
                system.activateCarPowerCutter()
                send_q.put(command.ok())
            elif command.action == 'power_cut_off_deactivate':
                print("Disabling Power cut...")
                system.deactivateCarPowerCutter()
                send_q.put(command.ok())
            elif command.action == 'buzzer_activate':
                print("Enabling buzzer...")
                system.activateBuzzer()
                send_q.put(command.ok())
            elif command.action == 'buzzer_deactivate':
                print("Disabling buzzer...")
                system.deactivateBuzzer()
                send_q.put(command.ok())
            elif command.action == 'call':
                print("Making a call...")
                send_q.put(command.ok())
                system.makeCall(command.args.get('number'))
            elif command.action == 'system_activate':
                print("Enabling system...")
                system_on = True
                send_q.put(command.ok())
            elif command.action == 'system_deactivate':
                print("Disabling system...")
                system_on = False
                send_q.put(command.ok())
        time.sleep(5)
        




if __name__ == "__main__":
    system.checkSerialPorts()
    for pir in system.pir:
        pir.when_motion = motionDetected
    send_q = queue.Queue()
    action_q = queue.Queue()
    send_t = Thread(target=sendCommand)
    action_t = Thread(target=actionLoop)

    pusher.connection.bind('pusher:connection_established', pusher_connect_handler)
    pusher.connect()
    
    

    send_t.start()
    action_t.start()

    
    send_t.join()
    action_t.join()

    
