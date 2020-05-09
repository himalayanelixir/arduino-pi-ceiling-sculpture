#!/home/pi/controller_env/bin/python3
# Copyright 2020 Harlen Bains
# linted using pylint
# formatted using black
"""This program restarts the Raspberry Pi safely. It uses the restart function
  from button.py and blinks the button leds 3 times before restarting.
"""

import os
import RPi.GPIO as GPIO  # pylint: disable=import-error
from button import restart


def main():
    """Restarts the Raspberry Pi
    """
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    led_pin = 23
    GPIO.setup(led_pin, GPIO.OUT)
    os.system("sudo systemctl stop button.service")
    restart(led_pin)


if __name__ == "__main__":
    main()
