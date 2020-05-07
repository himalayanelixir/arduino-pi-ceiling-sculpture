#!/root/gui_env/bin/python3
# Copyright 2020 Harlen Bains
# linted using pylint
# formatted using black
"""This program activates leds that show the network and firewall status of the
  Raspberry Pi. The LEDs blink to show that the Raspberry Pi isn't frozen.
"""

import time
import socket
import os
import RPi.GPIO as GPIO  # pylint: disable=import-error


def get_network_status():
    """Gets local ip address to determine if Raspberry Pi is connected to a
      network.

    Returns:
      Boolean saying whether or not the Raspberry Pi is connected to a network.
    """
    pi_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't have to be reachable
        pi_socket.connect(("10.255.255.255", 1))
        # can get local ip from _
        _ = pi_socket.getsockname()[0]
        is_connected = True
    except socket.error:
        is_connected = False
    finally:
        pi_socket.close()
    return is_connected


def get_firewall_status():
    """Gets ufw status

    Returns:
      Boolean saying whether or not the ufw firewall is active.
    """
    response = os.system("sudo ufw status | grep -qw active")
    return not bool(response)


def status_good(pins, toggle):
    """Sets GPIO pins for good status.

    Args:
      pins: Truple containing the pin values for the RGB LED we are updating.
      toggle: Current toggle value.
    """
    if toggle:
        GPIO.output(pins[0], GPIO.LOW)
        GPIO.output(pins[1], GPIO.LOW)
        GPIO.output(pins[2], GPIO.HIGH)
    else:
        GPIO.output(pins[0], GPIO.HIGH)
        GPIO.output(pins[1], GPIO.LOW)
        GPIO.output(pins[2], GPIO.HIGH)


def status_error(pins, toggle):
    """Sets GPIO pins for error status.

    Args:
      pins: Truple containing the pin values for the RGB LED we are updating.
      toggle: Current toggle value.
    """
    if toggle:
        GPIO.output(pins[0], GPIO.HIGH)
        GPIO.output(pins[1], GPIO.LOW)
        GPIO.output(pins[2], GPIO.LOW)
    else:
        GPIO.output(pins[0], GPIO.HIGH)
        GPIO.output(pins[1], GPIO.HIGH)
        GPIO.output(pins[2], GPIO.LOW)


def main():
    """Displays Raspberry Pi's status on to a screen
    """
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    toggle = True
    # pins are in RGB order
    led_network_pins = (16, 20, 21)
    led_firewall_pins = (18, 23, 24)
    for pin in led_network_pins:
        GPIO.setup(pin, GPIO.OUT)
    for pin in led_firewall_pins:
        GPIO.setup(pin, GPIO.OUT)
    while True:
        if get_firewall_status():
            status_good(led_firewall_pins, toggle)
        else:
            status_error(led_firewall_pins, toggle)
        if get_network_status():
            status_good(led_network_pins, toggle)
        else:
            status_error(led_network_pins, toggle)
        toggle = not toggle
        time.sleep(1)


if __name__ == "__main__":
    main()
