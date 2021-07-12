#from playsound import playsound

from config import Config
config = Config('config.ini').getConfig()

if __name__ == "__main__":
    print(config.sections())