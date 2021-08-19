import configparser
import os.path

class Config:
    def __init__(self,filename):
        self.filename = filename
        self.config_parser = configparser.ConfigParser()
        if not os.path.isfile(filename):
            self.createFile()
        self.config_parser.read(filename)

        self.BASE_URL = self.config_parser['DEFAULT']['base_url']
        self.TOKEN = self.config_parser['DEFAULT']['token']
        self.VEHICLE_ID = self.config_parser['DEFAULT']['vehicle_id']
        self.PUSHER = self.config_parser['DEFAULT']['pusher']
        self.PUSHER_PORT = self.config_parser['DEFAULT']['pusher_port']
        self.PUSHER_KEY = self.config_parser['DEFAULT']['pusher_key']
        self.PUSHER_SECRET = self.config_parser['DEFAULT']['pusher_secret']
        self.GPS_PORT = self.config_parser['ports']['gps_serial_port']
        self.SIM_PORT = self.config_parser['ports']['sim_serial_port']
        self.PIR1_PORT = int(self.config_parser['ports']['pir1_gpio_port'])
        self.PIR2_PORT = int(self.config_parser['ports']['pir2_gpio_port'])
        self.PIR3_PORT = int(self.config_parser['ports']['pir3_gpio_port'])
        self.BUZZER_PORT = int(self.config_parser['ports']['buzzer_gpio_port'])
        self.SIM_POWER_PIN = int(self.config_parser['ports']['sim_power_gpio_port'])
        self.CAR_POWER_PIN = int(self.config_parser['ports']['car_power_gpio_port'])
        self.MODEM_1 = self.config_parser['internet']['MODEM_1']
        self.MODEM_2 = self.config_parser['internet']['MODEM_2']
    def getConfig(self):
        return self.config_parser

    def createFile(self):
        self.config_parser['DEFAULT'] = {'base_url': 'http://safetocar.cl','token': '','vehicle_id': '','pusher':'safetocar.cl','pusher_port': '8082','pusher_key': 'key','pusher_secret': 'secret'}
        self.config_parser['media'] = {'backup_folder': 'backup'}
        self.config_parser['ports'] = {'gps_serial_port':'/dev/ttyUSB0','sim_serial_port':'/dev/ttyAMA0','pir1_gpio_port': 17,'pir2_gpio_port': 18,'pir3_gpio_port': 27,'buzzer_gpio_port': 22,'sim_power_gpio_port': 24,'car_power_gpio_port': 23}
        self.config_parser['internet'] = {'modem_1': 'eth1', 'modem_2': 'eth2'}
        with open(self.filename, 'w') as configfile:
            self.config_parser.write(configfile)
    
    def setTokenAndId(self,token,id):
        self.config_parser['DEFAULT']['token'] = token
        self.config_parser['DEFAULT']['vehicle_id'] = str(id)
        with open(self.filename, 'w') as configfile:
            self.config_parser.write(configfile)

