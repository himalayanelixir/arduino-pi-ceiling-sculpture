#!/home/pi/code/pi_env/bin/python3
# Copyright 2020 Harlen Bains
# linted using pylint
# formatted using black
"""This program shutsdown the Raspberry Pi safely. It uses the shutdown function
  from button.py and blinks the button leds 5 times before shutting down.
"""

import os
import RPi.GPIO as GPIO  # pylint: disable=import-error
import questionary  # pylint: disable=import-error
from button import shutdown


def main():
    """Shutsdown the Raspberry Pi
    """
    print(
        """\033[96m         __          __      __                  """
    )  # pylint: disable=anomalous-backslash-in-string
    print(
        """   _____/ /_  __  __/ /_____/ /___ _      ______ """
    )  # pylint: disable=anomalous-backslash-in-string
    print(
        """  / ___/ __ \/ / / / __/ __  / __ \ | /| / / __ \ """
    )  # pylint: disable=anomalous-backslash-in-string
    print(
        """ (__  ) / / / /_/ / /_/ /_/ / /_/ / |/ |/ / / / /"""
    )  # pylint: disable=anomalous-backslash-in-string
    print(
        """/____/_/ /_/\__,_/\__/\__,_/\____/|__/|__/_/ /_/ \033[0m"""
    )  # pylint: disable=anomalous-backslash-in-string
    input_text = questionary.select(
        "Do you want to shutdown the Raspberry Pi?", choices=["Yes", "No"]
    ).ask()
    if input_text == "Yes":
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        led_pin = 23
        GPIO.setup(led_pin, GPIO.OUT)
        os.system("sudo systemctl stop button.service")
        shutdown(led_pin)


if __name__ == "__main__":
    main()
