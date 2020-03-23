def waitForArduino(port):

    # wait until the Arduino sends 'Arduino Ready' - allows time for Arduino reset
    # it also ensures that any bytes left over from a previous message are discarded

    global startMarker, endMarker

    msg = ""
    while msg.find("Arduino is ready") == -1:
        while ser[port].inWaiting() == 0:
            pass
        msg = recvFromArduino(port)
        print("Arduino Number:", port, "Is Ready")
        print("Message from Arduino:" + msg)


def recvFromArduino(port):
    global startMarker, endMarker

    ck = ""
    x = "z"  # any value that is not an end- or startMarker
    # byteCount = -1 # to allow for the fact that the last increment will be one too many
    x = ser[port].read()
    x = x.decode("utf-8")
    # print(x)
    # wait for the start character
    while ord(x) != startMarker:
        x = ser[port].read()
        x = x.decode("utf-8")
        # print(x)
    # save data until the end marker is found
    while ord(x) != endMarker:
        if ord(x) != startMarker:
            ck = ck + x
            # byteCount += 1
        x = ser[port].read()
        x = x.decode("utf-8")
        # print(x)
    return ck


def run(td, port):
    waitingForReply = False

    if waitingForReply == False:
        ser[port].write(td.encode())
        print("-> -> -> -> -> ->")
        print("Thread: " + str(port) + " started")
        print("Message Sent:")
        print("PC: " + td)
        waitingForReply = True

    if waitingForReply == True:

        while ser[port].inWaiting() == 0:
            pass

        dataRecvd = recvFromArduino(port)
        print("<- <- <- <- <- <-")
        print("Thread: " + str(port) + " complete")
        print("Message Received:  " + dataRecvd)
        waitingForReply = False
        time.sleep(0.1)


def lintDesiredState():
    # Note here we are using commands_state.csv as a buffer as we lint desired_state.csv
    # Didn't want to have an extra file just to store the temp values

    desired_state = open("desired_state.csv", "r")
    commands_state = open("commands_state.csv", "w")

    desired_state_reader = csv.reader(desired_state, delimiter=",")
    commands_state_writer = csv.writer(commands_state)

    for desired_state_row in desired_state_reader:
        diff = [None] * NUMBER_OF_MOTORS_IN_ARRAY
        for i in range(NUMBER_OF_MOTORS_IN_ARRAY):
            if int(desired_state_row[i]) < 0:
                diff[i] = "0"
            elif int(desired_state_row[i]) > MAX_TURNS:
                diff[i] = str(MAX_TURNS)
            else:
                diff[i] = desired_state_row[i]
        commands_state_writer.writerow(diff)
    desired_state.close()
    commands_state.close()
    shutil.copy("commands_state.csv", "desired_state.csv")


def getDiff():
    current_state = open("current_state.csv", "r")
    desired_state = open("desired_state.csv", "r")
    commands_state = open("commands_state.csv", "w")

    current_state_reader = csv.reader(current_state, delimiter=",")
    desired_state_reader = csv.reader(desired_state, delimiter=",")
    commands_state_writer = csv.writer(commands_state)

    for current_state_row in current_state_reader:

        # used to iterate through the other file.
        desired_state_row = next(desired_state_reader)

        # zero the array we use to store the diffed
        # values which we will write to commands_state.csv
        diff = [None] * NUMBER_OF_MOTORS_IN_ARRAY

        # Uncomment for debug
        # print (current_state_row)
        # print (desired_state_row)

        # Construct output line
        for i in range(NUMBER_OF_MOTORS_IN_ARRAY):
            diff[i] = str(int(desired_state_row[i]) - int(current_state_row[i]))

        # Write the output file
        commands_state_writer.writerow(diff)

    print("<- <- <- <- <- <-")

    current_state.close()
    desired_state.close()
    commands_state.close()


def getCommands():

    global command_string
    command_string = ""

    commands_state = open("commands_state.csv", "r")
    commands_state_reader = csv.reader(commands_state, delimiter=",")
    # Reset the command string
    for commands_state_row in commands_state_reader:
        for i in range(NUMBER_OF_MOTORS_IN_ARRAY):
            if int(commands_state_row[i]) < 0:
                command_string += "Down,"
                command_string += str(abs(int(commands_state_row[i]))) + ","
            elif int(commands_state_row[i]) == 0:
                command_string += "None,"
                command_string += str(abs(int(commands_state_row[i]))) + ","
            elif int(commands_state_row[i]) > 0:
                command_string += "Up,"
                command_string += str(abs(int(commands_state_row[i]))) + ","
        # The code adds an extra comma to the end of a row, so we remove it here
        command_string = command_string[:-1]
        command_string += ";"

    # The code adds an extra semicolon to the very end of the string, so we remove it here
    command_string = command_string[:-1]
    # print(command_string)
    commands_state.close()


def executeCommands():
    parse_text = command_string.split(";")
    print(parse_text)

    # # create threads
    # for x in range(len(parse_text)):
    #     threads[x] = Thread(target=run, args=(parse_text[x], x))

    # # start threads
    # for x in range(len(parse_text)):
    #     threads[x].start()

    # # wait for threads to finish
    # for x in range(len(parse_text)):
    #     threads[x].join()


def updateCurrentState():
    shutil.copy("desired_state.csv", "current_state.csv")


def getResetDiff():
    commands_state = open("commands_state.csv", "w")
    commands_state_writer = csv.writer(commands_state)
    for x in range(NUMBER_OF_ARRAYS):
        # zero the array we use to store the diffed
        # values which we will write to commands_state.csv
        diff = [None] * NUMBER_OF_MOTORS_IN_ARRAY
        for i in range(NUMBER_OF_MOTORS_IN_ARRAY):
            diff[i] = 0
        commands_state_writer.writerow(diff)
    commands_state.close()


def getResetCommands():
    global command_string
    command_string = ""

    commands_state = open("commands_state.csv", "r")
    commands_state_reader = csv.reader(commands_state, delimiter=",")
    # Reset the command string
    for commands_state_row in commands_state_reader:
        for i in range(NUMBER_OF_MOTORS_IN_ARRAY):
            command_string += "Up,"
            command_string += "100,"
        # The code adds an extra comma to the end of a row, so we remove it here
        command_string = command_string[:-1]
        command_string += ";"

    # The code adds an extra semicolon to the very end of the string, so we remove it here
    command_string = command_string[:-1]
    print(command_string)
    commands_state.close()


def updateResetCurrentState():
    current_state = open("current_state.csv", "w")
    current_state_writer = csv.writer(current_state)
    for x in range(NUMBER_OF_ARRAYS):
        # zero the array we use to store the diffed
        # values which we will write to commands_state.csv
        diff = [None] * NUMBER_OF_MOTORS_IN_ARRAY
        for i in range(NUMBER_OF_MOTORS_IN_ARRAY):
            diff[i] = 0
        current_state_writer.writerow(diff)
    current_state.close()


# ======================================

import serial
import time
import sys
import shutil
import csv
from threading import Thread

# global variables
NUMBER_OF_ARRAYS = 2
NUMBER_OF_MOTORS_IN_ARRAY = 22
MAX_TURNS = 50
startMarker = 60
endMarker = 62
baudRate = 9600
# alternative serPort = "/dev/ttyUSB0"
serPort = ["/dev/cu.usbmodem1412101", "/dev/cu.usbmodem1412201"]
go = 1
diff = [None] * NUMBER_OF_MOTORS_IN_ARRAY
command_string = ""
parse_text = ""

# # initialize serial variable array and threads
# ser = [None] * NUMBER_OF_SLAVES
# threads = [None] * NUMBER_OF_SLAVES

# for x in range(len(serPort)):
#     ser[x] = serial.Serial(serPort[x], baudRate)
#     print("Serial port " + serPort[x] + " opened")

# print("")

# for port in range(len(serPort)):
#     waitForArduino(port)


while go == 1:
    print("===========")
    print("")
    text = input("Set ceiling (0), reset (1), or exit (2): ")
    if text == "0":
        lintDesiredState()
        # getDiff()
        # getCommands()
        # executeCommands()
        # updateCurrentState()
    elif text == "1":
        getResetDiff()
        getResetCommands()
        executeCommands()
        updateResetCurrentState()
    elif text == "2":
        go = 0
    else:
        print("Invalid Input")

# # close all serial connections
# for x in range(len(serPort)):
#     print("Serial port " + serPort[x] + " closed")
#     ser[x].close
