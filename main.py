from gpiozero import MotionSensor,Buzzer
from threading import *
from multiprocessing import Process
import subprocess
import time
import queue
import json
import os
import requests
import pickle
import pysher

from web import runApp
from config import Config
from system import System
from command import Command


config = Config('config.ini')
system = System(config)
system_on = False
power_cut_off = False

pusher = pysher.Pusher(config.PUSHER_KEY,secure=False,custom_host=config.PUSHER,port=config.PUSHER_PORT,secret=config.PUSHER_SECRET,auto_sub=True)
CHANNEL_ID = 'private-vehicle.'+str(config.VEHICLE_ID)


api = requests.Session()
api.headers.update({"Authorization":"Bearer "+config.TOKEN,"Accept": "application/json"})





def alive():
    """Process to send every 1 minute an alive command to the server,
    to mantain the connection and store actual status of the system
    """
    while True:
        r = api.post(config.BASE_URL+'/api/vehicle/alive',json=system.status(system_on))
        print("Sending ALIVE")
        time.sleep(60*1) # Waits for 1 minute

def getLastState():
    """This function is used on the main function, it runs once,
    it asks the server the last status setted in the server by the user.
    So, if the device lost connection or power, it can restore the last
    state.
    """
    global system_on
    r = api.get(config.BASE_URL+'/api/vehicle/state')
    state = r.json()
    if r.ok:
        system_on = state.get('system')
        if state.get('buzzer'):
            system.activateBuzzer()
        if state.get('cut_off_power'):
            system.activateCarPowerCutter()




def pusher_connect_handler(data):
    """Pusher connection handler,
    when the device connects to the pusher server,
    and returns the socket_id
    it has to register to the main server

    Args:
        data (String): The data returned from the pusher
        server
    """
    data = json.loads(data)
    auth = register(data.get('socket_id'),CHANNEL_ID)
    if auth:
        channel = pusher.subscribe(CHANNEL_ID,auth=auth)
        channel.bind('action', receiveCommand)


    







def register(socket_id,channel):
    """The server needs the device to register everytime to the channel to start receiving
    commands, so it makes a POST request to the server and the server must return an auth
    token to use in the pusher connection 

    Args:
        socket_id (String): The socket id of the pusher connection
        channel (String): The channel name used in the pusher connection

    Returns:
        String or None: Auth token if received or None
    """
    data = {
        'socket_id': socket_id,
        'channel_name': channel
        }
    r = api.post(config.BASE_URL+'/broadcasting/auth',data)
    if r.ok:
        return r.json()['auth']
    return None

def motionDetected():
    global system_on
    if system_on:
        send_q.put(Command.motionCommand())

def sendCommand():
    """One of the many Threads used in the program,
    Used to send commands to the server, uses the SEND QUEUE
    and make a POST request to the server with the info
    """
    while True:
        command = send_q.get()
        if command:
            print(command.toObject())
            r = api.post(config.BASE_URL+'/api/vehicle/action',json=command.toObject())
            print(r.text)
            print('Command Sended: action:{} status: {}'.format(command.action,r.status_code))


def receiveCommand(data):
    """Handler function used when a new command is received as text,
    but the program needs to be a command class, so it transforms to new 
    object and sends it to the action Queue

    Args:
        data (string): Text received from the server
    """
    data = json.loads(data).get('status')
    if data:
        command = Command.fromJson(data)
        action_q.put(command)



        
def actionLoop():
    """Process to execute the different commands received from the server
    such as take a picture, obtain GPS coordinates, cut the car power, activate
    the buzzer, make a call and activate/deactivate the pir sensors.
    When the command is received, it has to send an OK command to the server to advise
    that the command is received perfect. And when the action is done puts the response
    in the SEND Queue.
    """
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
                location = system.getLocation()
                if location:
                    send_q.put(command.gps(location[0], location[1]))
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
                system.makeCall(command.args.get('phone'))
            elif command.action == 'system_activate':
                print("Enabling system...")
                system_on = True
                send_q.put(command.ok())
            elif command.action == 'system_deactivate':
                print("Disabling system...")
                system_on = False
                send_q.put(command.ok())
        time.sleep(2)
        




if __name__ == "__main__":
    """Main process, first checks if the SIM808 is powered on,
    if not it powers on. Then starts the many threads and queue needed
    for the system.
    Lastly, starts the pusher connection to the server and activates the
    web server if the lan cable is connected to eth0 (the ethernet port of
    the raspberry)
    """
    if not system.checkSIM():
        print("MODEM NOT POWERED ON...")
        system.toggleSIM()
        time.sleep(5)
        if not system.checkSIM():
            exit(1)
        else:
            print("MODEM POWERED")
    
    
    system.checkSerialPorts()

    for pir in system.pir: # Setups the motion handler for every pir sensor
        pir.when_motion = motionDetected

    # Start the queues
    send_q = queue.Queue()
    action_q = queue.Queue()

    # Start the threads
    send_t = Thread(target=sendCommand)
    action_t = Thread(target=actionLoop)
    alive_t = Thread(target=alive)

    # Connects to the server using pusher connection
    pusher.connection.bind('pusher:connection_established', pusher_connect_handler)
    pusher.connect()


    # If the lan cable is connected, it starts the web config server
    if system.checkInterface('eth0'):
        print("LAN CABLE Connected...running config webserver")
        server = Process(target=runApp)
        server.start()
    

    # When the program was started, checks the last state
    # from the server.
    getLastState()

    send_t.start()
    action_t.start()
    alive_t.start()

    
    send_t.join()
    action_t.join()
    alive_t.join()

    
