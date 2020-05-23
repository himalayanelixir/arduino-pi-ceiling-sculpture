#!/home/pi/code/pi_env/bin/python3
# Copyright 2020 Harlen Bains
# linted using pylint
# formatted using black
"""This program restarts the Raspberry Pi safely. It uses the restart function
  from button.py and blinks the button leds 3 times before restarting.
"""

import os
import RPi.GPIO as GPIO  # pylint: disable=import-error
import questionary  # pylint: disable=import-error
from button import restart


def main():
    """Restarts the Raspberry Pi
    """
    print(
        """\033[96m                   __             __ """
    )  # pylint: disable=anomalous-backslash-in-string
    print(
        """   ________  _____/ /_____ ______/ /_"""
    )  # pylint: disable=anomalous-backslash-in-string
    print(
        """  / ___/ _ \/ ___/ __/ __ `/ ___/ __/"""
    )  # pylint: disable=anomalous-backslash-in-string
    print(
        """ / /  /  __(__  ) /_/ /_/ / /  / /_  """
    )  # pylint: disable=anomalous-backslash-in-string
    print(
        """/_/   \___/____/\__/\__,_/_/   \__/  \033[0m"""
    )  # pylint: disable=anomalous-backslash-in-string
    input_text = questionary.select(
        "Do you want to restart the Raspberry Pi?", choices=["Yes", "No"]
    ).ask()
    if input_text == "Yes":
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        led_pin = 23
        GPIO.setup(led_pin, GPIO.OUT)
        os.system("sudo systemctl stop button.service")
        restart(led_pin)


if __name__ == "__main__":
    main()
