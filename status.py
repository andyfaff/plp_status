import configparser
import time
import pathlib
import os.path
import requests


class Messenger(object):
    def __init__(self):
        config = configparser.ConfigParser()
        home_dir = str(pathlib.Path.home())
        ini_pth = os.path.join(home_dir, 'slack.ini')
        config.read(ini_pth)
        self.__slack_url = config['SLACK']['URL']

    def __call__(self, msg):
        pass


def status_loop():
    messenger = Messenger()

    while True:
        # check status, possibly send message
        time.sleep(30)


if __name__ == "__main__":
    status_loop()
