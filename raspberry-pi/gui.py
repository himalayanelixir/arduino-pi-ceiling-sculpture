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
import curses


def get_date_time():
    """Get the date and time in UTC.

    Returns:
      Date and time in UTC.
    """
    now = datetime.now()
    date_time = now.strftime("%d/%m/%Y %H:%M:%S")
    date_time = "Current Time: " + date_time + " UTC"
    return date_time


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
    except socket.error:
        ip_address = "Not Connected"
    finally:
        pi_socket.close()
    ip_address = "Local Internet: " + ip_address
    return ip_address


def get_internet_status():
    """Get internet status by pinging 8.8.8.8 (Google DNS).

    Returns:
      String saying whether or not the Raspberry Pi is connected to the internet.
    """
    response = os.system("ping -c 1 -w2 " + "8.8.8.8" + " > /dev/null 2>&1")
    if response == 0:
        internet_connection = "Public Internet: Connected"
    else:
        internet_connection = "Public Internet: Disconnected"
    return internet_connection


def main():
    """Displays Raspberry Pi's status on to a screen"""
    # initialize curses
    scr = curses.initscr()
    # remove cursor
    curses.curs_set(0)
    # loop forever updating the screen in 1 second increments
    # displays time, ip address, and internet connectivity
    while True:
        scr.addstr(7, 5, get_date_time(), curses.A_BOLD)
        scr.addstr(9, 5, get_ip(), curses.A_BOLD)
        scr.addstr(11, 5, get_internet_status(), curses.A_BOLD)
        scr.refresh()
        time.sleep(1)


if __name__ == "__main__":
    main()
