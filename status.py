import configparser
import time
import pathlib
import os.path
import datetime
import json
import requests


class Messenger(object):
    def __init__(self, web_hook_url):
        self.__web_hook_url = web_hook_url

    def __call__(self, msg):
        slack_msg = f"{datetime.datetime.now()}: {msg}"
        try:
            r = requests.post(
                self.__web_hook_url,
                data=json.dumps({"text": slack_msg}),
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            return r.status_code == requests.codes.ok
        except requests.exceptions.RequestException:
            return False


class Status():
    def __init__(self, status_url):
        self.__status_url = status_url
        self.status_dct = {"Power": 0.0, "CNS Out": 298}

    def update(self):
        """
        Update the Status.status_dct attribute.
        
        Returns
        -------
        response_code: bool
            Whether the status update request succeeded.
        """
        response = requests.get(self.__status_url, timeout=10)
        if response.ok:
            # something like
            # 'Power: 0.79144747996330261; CNS Out: 24.579999923706055; TG123: 1; CG123: 1; TG4: Open; HB1: 0; HB2: 1'
            dct = {}
            txt = response.text
            nums = ['Power', "CNS Out", "TG123", "CG123", "HB1", "HB2"]
            for tok in txt.split("; "):
                k, v = tok.split(":")
                if k in nums:
                    dct[k] = float(v)
                else:
                    dct[k] = v

            self.status_dct.update(dct)

        return response.ok


def status_loop():
    config = configparser.ConfigParser()
    home_dir = str(pathlib.Path.home())
    ini_pth = os.path.join(home_dir, 'slack.ini')
    config.read(ini_pth)
    web_hook_url = config['SLACK']['SLACK_URL']
    status_url = config['SLACK']['STATUS_URL']

    messenger = Messenger(web_hook_url)
    status = Status(status_url)
    status_dct = status.status_dct

    reactor_was_at_power = False
    CNS_was_cold = False

    while True:
        # check status, possibly send message
        try:
            updated = status.update()
        except requests.exceptions.RequestException:
            # might be a web outage
            updated = False

        if updated:
            # status update was successful
            power = status_dct["Power"]
            CNStemp = status_dct["CNS Out"]

            if power > 12:
                # reactor was at power, so monitor for transition
                reactor_was_at_power = True

            if reactor_was_at_power and power < 11:
                # reactor was above 12 MW, but now it's gone below 11.

                # set flag to False so we don't send repeated messages
                reactor_was_at_power = False
                msg = f"reactor power fell below 11 MW, ({power})"
                print(msg)
                messenger(msg)

            # TODO fix temperature limits
            if CNStemp < 26.5:
                CNS_was_cold = True

            if CNS_was_cold and CNStemp > 30:
                # set flag to False so we don't send repeated messages
                CNS_was_cold = False
                msg = f"CNS temperature = {CNStemp}"
                print(msg)
                messenger(msg)

            print(f"{datetime.datetime.now()}")
            print(status_dct)

        time.sleep(60)


if __name__ == "__main__":

    status_loop()
