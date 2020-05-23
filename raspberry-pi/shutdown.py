#!/home/pi/code/pi_env/bin/python3
# Copyright 2020 Harlen Bains
# linted using pylint
# formatted using black
"""This program shutsdown the Raspberry Pi safely. It uses the shutdown function
  from button.py and blinks the button leds 5 times before shutting down.
"""

from button import shutdown


def main():
    """Shutsdown the Raspberry Pi
    """
    shutdown(23)


if __name__ == "__main__":
    main()
