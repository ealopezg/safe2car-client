import pysher
import sys
import time
import json
# Add a logging handler so we can see the raw communication data
import logging
import requests

root = logging.getLogger()
root.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
root.addHandler(ch)
BASE_URL = 'http://safetocar.cl'
token = '1|Sze0mZUqQ4h8eVGGtRgA7klG2eAhgeBfI5uktU5f'
channel_id = 'private-vehicle.1'
pusher = pysher.Pusher('key',secure=False,custom_host="147.182.130.16",port="8082",secret="secret")

s = requests.Session()
s.headers.update({"Authorization":"Bearer "+token,"Accept": "application/json"})

def  my_func(*args, **kwargs):
    print("processing Args:", json.loads(args[0]))
    print("processing Kwargs:", kwargs)


def register(socket_id,channel):
    data = {
        'socket_id': socket_id,
        'channel_name': channel
        }
    r = s.post(BASE_URL+'/broadcasting/auth',data)
    return r.json()['auth']
# We can't subscribe until we've connected, so we use a callback handler
# to subscribe when able
def connect_handler(data):
    data = json.loads(data)
    print(data['socket_id'])
    auth = register(data.get('socket_id'),channel_id)
    channel = pusher.subscribe(channel_id,auth=auth)
    channel.bind('action', my_func)

pusher.connection.bind('pusher:connection_established', connect_handler)
pusher.connect()

while True:
    # Do other things in the meantime here...
    time.sleep(1)