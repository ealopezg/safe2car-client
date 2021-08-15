from command import Command
from picamera import PiCamera
from datetime import datetime
from io import BytesIO
import time
def takePicture(save=False):
    stream = BytesIO()
    camera = PiCamera()
    camera.start_preview()
    time.sleep(2)
    camera.capture(stream, 'jpeg')
    timestamp = datetime.timestamp(datetime.now())
    if save:
        file = open("image_{}.jpg".format(timestamp),"wb")
        file.write(stream.getbuffer())
        file.close()
    command = Command.imageCommand(stream.getvalue())
    stream.close()
    camera.close()
    return command

