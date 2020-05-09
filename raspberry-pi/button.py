#!/home/pi/pi_env/bin/python3
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


def restart(led_pin):
    """Blinks leds 3 times and then restarts the Raspberry Pi

    Args:
      led_pin: The pin number where the led for the button is connected
    """
    for _ in range(0, 3):
        GPIO.output(led_pin, GPIO.LOW)
        time.sleep(0.25)
        GPIO.output(led_pin, GPIO.HIGH)
        time.sleep(0.25)
    os.system("sudo reboot")


def shutdown(led_pin):
    """Blinks leds 5 times and then shutsdown the Raspberry Pi

    Args:
      led_pin: The pin number where the led for the button is connected
    """
    for _ in range(0, 5):
        GPIO.output(led_pin, GPIO.LOW)
        time.sleep(0.25)
        GPIO.output(led_pin, GPIO.HIGH)
        time.sleep(0.25)
    os.system("sudo shutdown -h now")


def main():
    """Adds button and button LED functionality to Raspberry Pi
    """
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    counter = 0
    toggle = False
    button_pin = 18
    led_pin = 23
    GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(led_pin, GPIO.OUT)
    while True:
        if GPIO.input(button_pin) == GPIO.HIGH:
            if counter % 5 == 0:
                toggle = not toggle
            if toggle:
                GPIO.output(led_pin, GPIO.HIGH)
            else:
                GPIO.output(led_pin, GPIO.LOW)
            counter += 1
        else:
            GPIO.output(led_pin, GPIO.HIGH)
            if 25 <= counter < 45:
                restart(led_pin)
            elif counter >= 45:
                shutdown(led_pin)
            counter = 0
        time.sleep(0.10)


if __name__ == "__main__":
    main()
