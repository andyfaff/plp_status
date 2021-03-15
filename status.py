import configparser
import time
import requests


class Messenger(object):
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('slack.ini')
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
