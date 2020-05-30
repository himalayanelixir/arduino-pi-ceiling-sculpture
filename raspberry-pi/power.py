#!/home/pi/code/pi_env/bin/python3
# Copyright 2020 Harlen Bains
# linted using pylint
# formatted using black
"""This program allows the user to shutdown or restart a Raspberry Pi safely.
    It uses the shutdown and restart functions from button.py and blinks the
    button leds before restarting or shutting down
"""

import sys
import os
import RPi.GPIO as GPIO  # pylint: disable=import-error
import questionary  # pylint: disable=import-error
from button import shutdown
from button import restart


def shutdown_prompt():
    """Shutsdown the Raspberry Pi
    """
    print(
        """\033[96m         __          __      __                  """
    )  # pylint: disable=anomalous-backslash-in-string
    # pylint: disable=duplicate-code
    print(
        """   _____/ /_  __  __/ /_____/ /___ _      ______ """
    )  # pylint: disable=anomalous-backslash-in-string
    # pylint: disable=duplicate-code
    print(
        """  / ___/ __ \/ / / / __/ __  / __ \ | /| / / __ \ """
    )  # pylint: disable=anomalous-backslash-in-string
    print(
        """ (__  ) / / / /_/ / /_/ /_/ / /_/ / |/ |/ / / / /"""
    )  # pylint: disable=anomalous-backslash-in-string
    # pylint: disable=duplicate-code
    print(
        """/____/_/ /_/\__,_/\__/\__,_/\____/|__/|__/_/ /_/ \033[0m\n"""
    )  # pylint: disable=anomalous-backslash-in-string
    # pylint: disable=duplicate-code
    input_text = questionary.select(
        "Do you want to shutdown the Raspberry Pi?", choices=["Yes", "No"]
    ).ask()
    if input_text == "Yes":
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(LED_PIN, GPIO.OUT)
        os.system("sudo systemctl stop button.service")
        shutdown(LED_PIN)


def restart_prompt():
    """Restarts the Raspberry Pi
    """
    print(
        """\033[96m                   __             __ """
    )  # pylint: disable=anomalous-backslash-in-string
    print(
        """   ________  _____/ /_____ ______/ /_"""
    )  # pylint: disable=anomalous-backslash-in-string
    # pylint: disable=duplicate-code
    print(
        """  / ___/ _ \/ ___/ __/ __ `/ ___/ __/"""
    )  # pylint: disable=anomalous-backslash-in-string
    # pylint: disable=duplicate-code
    print(
        """ / /  /  __(__  ) /_/ /_/ / /  / /_  """
    )  # pylint: disable=anomalous-backslash-in-string
    # pylint: disable=duplicate-code
    print(
        """/_/   \___/____/\__/\__,_/_/   \__/  \033[0m\n"""
    )  # pylint: disable=anomalous-backslash-in-string
    # pylint: disable=duplicate-code
    input_text = questionary.select(
        "Do you want to restart the Raspberry Pi?", choices=["Yes", "No"]
    ).ask()
    if input_text == "Yes":
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(LED_PIN, GPIO.OUT)
        os.system("sudo systemctl stop button.service")
        restart(LED_PIN)


def main():
    """Looks at arguments passed to script and calls appropriate function
    """
    if sys.argv[1] == "shutdown":
        shutdown_prompt()
    elif sys.argv[1] == "restart":
        restart_prompt()
    else:
        print(f"Invalid Argument: {sys.argv[1]}")


LED_PIN = 23

if __name__ == "__main__":
    main()
