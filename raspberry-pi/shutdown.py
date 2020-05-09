#!/home/pi/controller_env/bin/python3
# Copyright 2020 Harlen Bains
# linted using pylint
# formatted using black
"""This program controls a push button with LEDs that allow a user to restart or
  shutdown the Raspberry Pi. Hold down for 3 blinks to restart and 5 to
  shutdown.
"""

import time
import os
import RPi.GPIO as GPIO  # pylint: disable=import-error
from button import shutdown


def main():
    """Displays Raspberry Pi's status on to a screen
    """
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    led_pin = 23
    GPIO.setup(led_pin, GPIO.OUT)
    shutdown(led_pin)

if __name__ == "__main__":
    main()
