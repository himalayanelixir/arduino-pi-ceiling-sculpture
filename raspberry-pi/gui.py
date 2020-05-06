#!/root/gui_env/bin/python3
# Copyright 2020 Harlen Bains
# linted using pylint
# formatted using black
"""This program creates a dashboard displaying the Pi's status. Displays time,
local IP address, and internet connectivity
"""

from datetime import datetime
import time
import socket
import os
import RPi.GPIO as GPIO

def get_ip():
    """Gets current local ip address of Raspberry Pi.

    Returns:
      Local IP address of the Raspberry Pi.
    """
    pi_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        pi_socket.connect(("10.255.255.255", 1))
        ip_address = pi_socket.getsockname()[0]
        is_connected = True
    except socket.error:
        is_connected = False
    finally:
        pi_socket.close()
    return is_connected


def get_internet_status():
    """Get internet status by pinging 8.8.8.8 (Google DNS).

    Returns:
      String saying whether or not the Raspberry Pi is connected to the internet.
    """
    response = os.system("ping -c 1 -w2 " + "8.8.8.8" + " > /dev/null 2>&1")
    if response == 0:
        internet_connection = True
    else:
        internet_connection = False
    return internet_connection


def main():
    """Displays Raspberry Pi's status on to a screen"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(20,GPIO.OUT)
    GPIO.setup(21,GPIO.OUT)
    GPIO.setup(23,GPIO.OUT)
    GPIO.setup(24,GPIO.OUT)
    while True:
        if get_internet_status():
            GPIO.output(23,GPIO.HIGH)
        else:
            GPIO.output(24,GPIO.HIGH)
        if get_ip():
            GPIO.output(21,GPIO.HIGH)
        else:
            GPIO.output(20,GPIO.HIGH)
        time.sleep(2)
        GPIO.output(20,GPIO.LOW)
        GPIO.output(21,GPIO.LOW)
        GPIO.output(23,GPIO.LOW)
        GPIO.output(24,GPIO.LOW)
        time.sleep(1)


if __name__ == "__main__":
    main()
