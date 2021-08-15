from datetime import datetime
import json
import base64

class Command:
    def __init__(self,action,args={},added_at=datetime.now().isoformat(),id=None):
        self.action = action
        self.id = id
        self.added_at = added_at
        self.args = args
            

    def __str__(self):
        return "Command: action:{},added_at: {}".format(self.action,self.added_at)

    def toObject(self):
        return {
                'id': self.id,
                'action': self.action,
                'added_at': self.added_at,
                'args': self.args
            }

    def photo(self,image):
        return Command('photo',args={"body":  base64.b64encode(image).decode('ascii')},id=self.id,added_at=self.added_at)

    def gps(self,latitude,longitude):
        return Command('location',args={"lat": latitude,"long": longitude},id=self.id)

    def ok(self):
        return Command('OK',id=self.id)

    @staticmethod
    def alive(status):
        return Command('alive',args=status)  

    @staticmethod
    def pirCommand():
        return Command('pir')  

    @staticmethod
    def fromJson(data):
        args = data.get('args')
        if not args:
            args = {}
        command = Command(data.get('action'),args,data.get('added_at'),data.get('id'))
        return command