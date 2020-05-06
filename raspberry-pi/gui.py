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

def status_good(pins, on_off):
    if on_off:
        GPIO.output(pins[0],GPIO.LOW)
        GPIO.output(pins[1],GPIO.LOW)
        GPIO.output(pins[2],GPIO.HIGH)
    else:
        GPIO.output(pins[0],GPIO.HIGH)
        GPIO.output(pins[1],GPIO.LOW)
        GPIO.output(pins[2],GPIO.HIGH)

def status_error(pins, on_off):
    if on_off:
        GPIO.output(pins[0],GPIO.HIGH)
        GPIO.output(pins[1],GPIO.LOW)
        GPIO.output(pins[2],GPIO.LOW)
    else:
        GPIO.output(pins[0],GPIO.HIGH)
        GPIO.output(pins[1],GPIO.HIGH)
        GPIO.output(pins[2],GPIO.LOW)

def main():
    """Displays Raspberry Pi's status on to a screen"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    led_network_pins = (16,20,21)
    led_firewall_pins = (18,23,24)
    for pin in led_network_pins:
        GPIO.setup(pin,GPIO.OUT)
    for pin in led_firewall_pins:
        GPIO.setup(pin,GPIO.OUT)
    while True:
        if get_internet_status():
            status_error(led_firewall_pins,True)
        else:
            status_good(led_firewall_pins,True)
        if get_ip():
            status_good(led_network_pins, True)
        else:
            status_error(led_network_pins,True)
        time.sleep(1)
        if get_internet_status():
            status_error(led_firewall_pins,False)
        else:
            status_good(led_firewall_pins,False)
        if get_ip():
            status_good(led_network_pins, False)
        else:
            status_error(led_network_pins,False)
        time.sleep(1)


if __name__ == "__main__":
    main()
