import configparser
import os.path

class Config:
    def __init__(self,filename):
        self.filename = filename
        self.config_parser = configparser.ConfigParser()
        if not os.path.isfile(filename):
            self.createFile()
        self.config_parser.read(filename)
    
    def getConfig(self):
        return self.config_parser

    def createFile(self):
        self.config_parser['DEFAULT'] = {'BaseUrl': '','Token': ''}
        self.config_parser['media'] = {'Alarm': 'resources/TF002.WAV','BackupFolder': 'backup'}
        self.config_parser['data'] = {'GpsCOMPort':78567,'SimCOMPort':3424}
        with open(self.filename, 'w') as configfile:
            self.config_parser.write(configfile)

