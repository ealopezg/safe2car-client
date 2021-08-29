from datetime import datetime
import json
import base64
import os
class Command:
    """Command class, it is used to receive and send command objects to
    and from the server
    """
    def __init__(self,action,args={},added_at=datetime.now().isoformat(),id=None):
        """Constructor

        Args:
            action (String): Action type
            args (dict, optional): The arguments from the command, it can be the phone number or the GPS coordinates. Defaults to {}.
            added_at (timestamp, optional): The time where the command is created. Defaults to datetime.now().isoformat().
            id (int, optional): The command id received from the server. Defaults to None.
        """
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
        """Method to create a photo command as a response for a command

        Args:
            image (Bytes): The content of the photo

        Returns:
            Command: The command 
        """
        return Command('photo',args={"body":  base64.b64encode(image).decode('ascii')},id=self.id,added_at=self.added_at)

    def gps(self,latitude,longitude):
        """Method to create a location command as a response for a command

        Args:
            latitude (float): The latitude obtained from the gps
            longitude (float): The longitude obtained from the gps

        Returns:
            Command: The command 
        """
        return Command('location',args={"lat": latitude,"long": longitude},id=self.id)

    def ok(self):
        """Method to create a OK command based on a command

        Returns:
            Command: The command 
        """
        return Command('OK',id=self.id)

    @staticmethod
    def motionCommand():
        """Static method to create a motion command as an alert

        Returns:
            Command: The command 
        """
        return Command('motion')  

    @staticmethod
    def fromJson(data):
        """Create a new command based on a dict object

        Args:
            data (dict): The dict with the command parameters

        Returns:
            Command: The command 
        """
        args = data.get('args')
        if not args:
            args = {}
        command = Command(data.get('action'),args,data.get('added_at'),data.get('id'))
        return command