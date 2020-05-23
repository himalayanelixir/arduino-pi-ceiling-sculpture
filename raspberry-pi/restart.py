#!/home/pi/code/pi_env/bin/python3
# Copyright 2020 Harlen Bains
# linted using pylint
# formatted using black
"""This program restarts the Raspberry Pi safely. It uses the restart function
  from button.py and blinks the button leds 3 times before restarting.
"""

from button import restart


def main():
    """Restarts the Raspberry Pi
    """
    restart(23)


if __name__ == "__main__":
    main()
