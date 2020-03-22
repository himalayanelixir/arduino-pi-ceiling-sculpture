#!/usr/bin/python3

import serial
import time
import sys
from threading import Thread
from yaspin import yaspin
from yaspin.spinners import Spinners
import timeout_decorator


def waitForArduino(port):
    global didErrorOccur
    # wait until the Arduino sends "Arduino Ready" - allows time for Arduino reset
    # it also ensures that any bytes left over from a previous message are discarded
    try:
        waitForArduinoExecute(port)
        spinner.write("Serial Port " + str(port) + " \033[32m" + "READY" + "\033[0m")
    except:
        spinner.write("Serial Port " + str(port) + " \033[31m" + "FAILED" + "\033[0m")
        didErrorOccur = True


@timeout_decorator.timeout(10, use_signals=False)
def waitForArduinoExecute(port):
    msg = ""
    while msg.find("Arduino is ready") == -1:
        while ser[port].inWaiting() == 0:
            pass
        msg = recvFromArduino(port)


def recvFromArduino(port):
    ck = ""
    # any value that is not an end- or startMarker
    x = "z"
    x = ser[port].read()
    x = x.decode("utf-8")
    # wait for the start character
    while ord(x) != startMarker:
        x = ser[port].read()
        x = x.decode("utf-8")
    # save data until the end marker is found
    while ord(x) != endMarker:
        if ord(x) != startMarker:
            ck = ck + x
        x = ser[port].read()
        x = x.decode("utf-8")
    return ck


def run(td, port):
    # wait until the Arduino sends "Arduino Ready" - allows time for Arduino reset
    # it also ensures that any bytes left over from a previous message are discarded
    try:
        runExecute(td, port)
    except:
        spinner.write(
            "== == Array: "
            + str(port)
            + " \033[31m"
            + "EXECUTION FAILED TIMEOUT"
            + "\033[0m"
        )


@timeout_decorator.timeout(100, use_signals=False)
def runExecute(td, port):
    waitingForReply = False
    if waitingForReply == False:
        ser[port].write(td.encode())
        spinner.write("-> -> Array: " + str(port) + " \033[32m" + "SENT" + "\033[0m")
        waitingForReply = True

    if waitingForReply == True:
        while ser[port].inWaiting() == 0:
            pass
        dataRecvd = recvFromArduino(port)
        spinner.write("<- <- Array: " + str(port) + " " + dataRecvd)
        waitingForReply = False


def errorCheck():
    if didErrorOccur == True:
        closeConnections()


def closeConnections():
    print("\nClosing Ports")
    spinner.start()
    for x in range(len(serPort)):
        try:
            ser[x].close
            spinner.write(
                "Serial port "
                + str(x)
                + " "
                + serPort[x]
                + " \033[32m"
                + "CLOSED"
                + "\033[0m"
            )
        except:
            spinner.write(
                "Serial port "
                + str(x)
                + " "
                + serPort[x]
                + " \033[31m"
                + "FAILED"
                + "\033[0m"
            )
            spinner.stop()
            pass
    spinner.stop()


# ======================================


# global variables
NUMBER_OF_SLAVES = 2
startMarker = 60
endMarker = 62
baudRate = 9600
serPort = ["/dev/ttyUSB0", "/dev/ttyUSB1"]
spinner = yaspin(Spinners.weather)
didErrorOccur = False

# initialize serial variable array
ser = [None] * NUMBER_OF_SLAVES
threads = [None] * NUMBER_OF_SLAVES
connectingThreads = [None] * NUMBER_OF_SLAVES

while True:
    didErrorOccur == False
    inputText1 = input("\n\nPress Enter to Start the Program or type 'Exit' to Close:")
    if inputText1 == "Exit" or inputText1 == "exit":
        break
    print("Opening Ports")
    spinner.start()
    for x in range(len(serPort)):
        try:
            ser[x] = serial.Serial(serPort[x], baudRate)
            spinner.write(
                "Serial Port "
                + str(x)
                + " "
                + serPort[x]
                + " \033[32m"
                + "READY"
                + "\033[0m"
            )
        except:
            spinner.write(
                "Serial Port "
                + str(x)
                + " "
                + serPort[x]
                + " \033[31m"
                + "FAILED"
                + "\033[0m"
            )
            spinner.stop()
            didErrorOccur = True
            pass
    spinner.stop()

    if didErrorOccur == False:
        print("\nConnecing to Arrays")
        spinner.start()
        # create threads
        for port in range(len(serPort)):
            connectingThreads[port] = Thread(target=waitForArduino, args=[port])

        # start threads
        for port in range(len(serPort)):
            connectingThreads[port].start()

        # wait for threads to finish
        for port in range(len(serPort)):
            connectingThreads[port].join()
        spinner.stop()

    if didErrorOccur == False:
        break
    else:
        errorCheck()

while inputText1 != "Exit" and inputText1 != "exit":
    print("===========\n")
    inputText2 = input("Enter Commands ('Exit' to close program): ")
    if inputText2 == "Exit" or inputText2 == "exit":
        # close all serial connections
        closeConnections()
        break
    parse_text = inputText2.split(";")
    spinner.start()
    # create threads
    for x in range(len(parse_text)):
        threads[x] = Thread(target=run, args=(parse_text[x], x))
    # start threads
    for x in range(len(parse_text)):
        threads[x].start()
    # wait for threads to finish
    for x in range(len(parse_text)):
        threads[x].join()
    spinner.stop()
