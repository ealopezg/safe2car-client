from pyroute2 import NDB
import requests
import xmltodict
import time
import socket
# Class from https://gitmemory.com/issue/arska/e3372/1/491995448
class HuaweiE3372(object):

    BASE_URL = 'http://{host}'
    TOKEN_URL = '/api/webserver/SesTokInfo'
    SWITCH_URL = '/api/dialup/mobile-dataswitch'
    session = None

    def __init__(self,host='192.168.8.1'):
        self.host = host
        self.base_url = self.BASE_URL.format(host=host)
        self.session = requests.Session()

    def status(self):
        try:
            self.session = requests.Session()
            # Get session and verification tokens from the modem
            r = self.session.get(self.base_url + self.TOKEN_URL, timeout=3)
            _dict = xmltodict.parse(r.text).get('response', None)

            # Build the switch request
            headers = {
            'Cookie': _dict['SesInfo'],
            '__RequestVerificationToken': _dict['TokInfo']
            }
            

            r = self.session.get(self.base_url + self.SWITCH_URL, headers=headers, timeout=3)
            

            if r.status_code == 200:
                resp = xmltodict.parse(r.text).get('response', None)
                if resp is not None:
                    return int(resp['dataswitch'])
                else:
                    return False
            else:
                return False

        except Exception as ex:
            print("Failed to get status..")
            print(ex)
            return False


    def switch_modem(self, state='1'):
        try:
            self.session = requests.Session()
            # Get session and verification tokens from the modem
            r = self.session.get(self.base_url + self.TOKEN_URL, timeout=3)
            _dict = xmltodict.parse(r.text).get('response', None)

            # Build the switch request
            headers = {
            'Cookie': _dict['SesInfo'],
            '__RequestVerificationToken': _dict['TokInfo']
            }
            
            data = '<?xml version: "1.0" encoding="UTF-8"?><request><dataswitch>' + state + '</dataswitch></request>'

            r = self.session.post(self.base_url + self.SWITCH_URL, data=data, headers=headers, timeout=3)
            if r.status_code == 200:
                return True
            else:
                return False

        except Exception as ex:
            print("Failed to switch modem..")
            print(ex)
            return False
    






class Network:
    def __init__(self):
        self.ndb = NDB()
    
    def swapInterface(self):
        ipx_old = self.ndb.interfaces[self.ndb.routes['default']['oif']]
        if ipx_old['ifname'] == 'eth2':
            ipx_new = self.ndb.interfaces['eth1']
            ipx_new.set('state','up').commit()
            ipx_old.set('state','down').commit()
        else:
            ipx_new = self.ndb.interfaces['eth2']
            ipx_new.set('state','up').commit()
            ipx_old.set('state','down').commit()
        time.sleep(10)
        h = HuaweiE3372()
        if h.status() == 0:
            h.switch_modem('1')
            time.sleep(5)
    
    def internet(self):
        try:
            socket.setdefaulttimeout(3)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(('8.8.8.8', 53))
            return True
        except Exception as ex:
            return False

    def turnOnModem(self):
        h = HuaweiE3372()
        if h.status() == 0:
            h.switch_modem('1')
            time.sleep(5)
    
    def checkModem(self):
        h = HuaweiE3372()
        return h.status() == 1



    


