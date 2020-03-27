#!/home/pi/controller_env/bin/python3

import serial
import time
import sys
import shutil
from threading import Thread
from yaspin import yaspin
from yaspin.spinners import Spinners
import timeout_decorator
import csv
import os.path
from os import path


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


def csvCommands():
    global commandString

    # lint desired_state csv values and make sure that they are in range
    desiredStateList = []
    with open("desired_state.csv", "r") as desiredStateFile:
        desiredStateReader = csv.reader(desiredStateFile, delimiter=",")
        desiredStateList = list(desiredStateReader)
    for countRow, row in enumerate(desiredStateList):
        for countColumn, column in enumerate(row):
            if int(column) > MAX_TURNS:
                desiredStateList[countRow][countColumn] = str(MAX_TURNS)
            elif int(column) < 0:
                desiredStateList[countRow][countColumn] = "0"
    with open("desired_state.csv", "w", newline="") as desiredStateFile:
        desiredStateWriter = csv.writer(desiredStateFile, quoting=csv.QUOTE_ALL)
        desiredStateWriter.writerows(desiredStateList)

    # fill command string
    commandString = ""
    desiredStateList = []
    currentStateList = []
    with open("desired_state.csv", "r") as desiredStateFile:
        desiredStateReader = csv.reader(desiredStateFile, delimiter=",")
        desiredStateList = list(desiredStateReader)
    with open("current_state.csv", "r", newline="") as currentStateFile:
        currentstateReader = csv.reader(currentStateFile, delimiter=",")
        currentStateList = list(currentstateReader)
    # assumption here is that both csvs are the size
    for countRow, row in enumerate(desiredStateList):
        commandString += "<"
        for countColumn, column in enumerate(row):
            difference = int(currentStateList[countRow][countColumn]) - int(
                desiredStateList[countRow][countColumn]
            )
            if difference < 0:
                commandString += "Down,"
            elif difference > 0:
                commandString += "Up,"
            else:
                commandString += "None,"
            commandString += str(abs(difference)) + ","
        commandString = commandString[:-1]
        commandString += ">;"
    # remove final semicolon
    commandString = commandString[:-1]
    # call execute commands
    executeCommands()
    # update current_state.csv with the values of desired_state.csv
    shutil.copy2('desired_state.csv', "current_state.csv")


def resetCommands():
    global commandString
    currentStateList = []
    commandString = ""
    with open("current_state.csv", "r") as currentStateFile:
        currentStateReader = csv.reader(currentStateFile, delimiter=",")
        currentStateList = list(currentStateReader)
    for countRow, row in enumerate(currentStateList):
        commandString += "<"
        for countColumn, column in enumerate(row):
            currentStateList[countRow][countColumn] = "0"
            commandString += "Up,100,"
        commandString = commandString[:-1]
        commandString += ">;"
    commandString = commandString[:-1]
    with open("current_state.csv", "w", newline="") as currentStateFile:
        currentStateWriter = csv.writer(currentStateFile, quoting=csv.QUOTE_ALL)
        currentStateWriter.writerows(currentStateList)
    # call execute commands
    executeCommands()


def executeCommands():
    parse_text = commandString.split(";")
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
NUMBER_OF_ARRAYS = 2
startMarker = 60
endMarker = 62
baudRate = 9600
serPort = ["/dev/ttyUSB0", "/dev/ttyUSB1"]
spinner = yaspin(Spinners.weather)
didErrorOccur = False

# initialize serial variable array
ser = [None] * NUMBER_OF_ARRAYS
threads = [None] * NUMBER_OF_ARRAYS
connectingThreads = [None] * NUMBER_OF_ARRAYS


# TODO: See if we actually use these
NUMBER_OF_MOTORS_IN_ARRAY = 22
MAX_TURNS = 10
commandString = ""
parse_text = ""


while True:
    didErrorOccur == False
    inputText1 = input("\n\nPress Enter to Start the Program or type 'Exit' to Close:")
    if inputText1 == "Exit" or inputText1 == "exit":
        break

    print("\nOpening Ports")
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
        print("\nChecking for CSV Files")
        if path.exists("current_state.csv"):
            print("current_state CSV: \033[32m FOUND\033[0m")
        else:
            print("current_state CSV: \033[31m NOT FOUND\033[0m")
            didErrorOccur = True
        if path.exists("desired_state.csv"):
            print("desired_state CSV: \033[32m FOUND\033[0m")
        else:
            print("desired_state CSV: \033[31m NOT FOUND\033[0m")
            didErrorOccur = True

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
    inputText2 = input(
        "Enter '1' to set ceiling from csv, '2' to reset, '3' for manual mode, and 'Exit' to close program)\n : "
    )
    # csv mode
    if inputText2 == "1":
        print("CSV Mode\n")
        csvCommands()
    # csv reset
    elif inputText2 == "2":
        print("CSV Reset Mode\n")
        resetCommands()
    # manual mode
    elif inputText2 == "3":
        print("Manual Mode\n")
        commandString = ""
        commandString = input("Enter Commands (format '<Up,1>;<Up,1>'):\n : ")
        executeCommands()
    # exit
    elif inputText2 == "Exit" or inputText2 == "exit":
        # close all serial connections
        closeConnections()
        break
    else:
        print("Invalid Input\n")
