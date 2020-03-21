from datetime import datetime
import time
import socket
import os
import curses

# gets date and time in UTC
def getDateTime():
    now = datetime.now()
    dtString = now.strftime("%d/%m/%Y %H:%M:%S")
    dtString = "Current Time: " + dtString + " UTC"
    return dtString


# gets current local ip address of raspberry pi
def getIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(("10.255.255.255", 1))
        ipAddress = s.getsockname()[0]
    except:
        ipAddress = "Not Connected"
    finally:
        s.close()
    ipAddress = "Local IP: " + ipAddress
    return ipAddress


# get internet starts by pinging 8.8.8.8 (google dns)
def getInternetStatus():
    response = os.system("ping -c 1 -w2 " + "8.8.8.8" + " > /dev/null 2>&1")
    if response == 0:
        internetConnection = "Internet: Connected"
    else:
        internetConnection = "Internet: Disconnected"
    return internetConnection


# initialize curses
scr = curses.initscr()
# remove cursor
curses.curs_set(0)
# loop forever updating the screen in 1 second increments
# displays time, ip address, and internet connectivity
while True:
    scr.addstr(7, 5, getDateTime(), curses.A_BOLD)
    scr.addstr(9, 5, getIP(), curses.A_BOLD)
    scr.addstr(11, 5, getInternetStatus(), curses.A_BOLD)
    scr.refresh()
    time.sleep(1)
