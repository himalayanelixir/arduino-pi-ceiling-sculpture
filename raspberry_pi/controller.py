#!/home/pi/controller_env/bin/python3
"""This script runs on the Raspberry Pi and sends commands to Arduinos.
Once a command is sent it then waits a reply"""

import csv
import shutil
from os import path
from threading import Thread
import serial
from yaspin import yaspin
from yaspin.spinners import Spinners
import timeout_decorator


def wait_for_arduino(port):
    """Wait until the Arduino sends "Arduino Ready" - allows time for Arduino
    reset it also ensures that any bytes left over from a previous message are
    discarded """
    global DID_ERROR_OCCUR
    try:
        wait_for_arduino_execute(port)
        SPINNER.write("Serial Port " + str(port) + " \033[32m" + "READY" + "\033[0m")
    except timeout_decorator.TimeoutError:
        SPINNER.write("Serial Port " + str(port) + " \033[31m" + "FAILED" + "\033[0m")
        DID_ERROR_OCCUR = True


@timeout_decorator.timeout(10, use_signals=False)
def wait_for_arduino_execute(port):
    """ Waits for Arduino to send ready message. Created so we can have a
    timeout and a try catch block"""
    msg = ""
    while msg.find("Arduino is ready") == -1:
        while SERIAL_OBJECT[port].inWaiting() == 0:
            pass
        msg = recieve_from_arduino(port)


def recieve_from_arduino(port):
    """ Gets message from Arduino"""
    recieve_string = ""
    # any value that is not an end- or START_MARKER
    recieve_char = "z"
    recieve_char = SERIAL_OBJECT[port].read()
    recieve_char = recieve_char.decode("utf-8")
    # wait for the start character
    while ord(recieve_char) != START_MARKER:
        recieve_char = SERIAL_OBJECT[port].read()
        recieve_char = recieve_char.decode("utf-8")
    # save data until the end marker is found
    while ord(recieve_char) != END_MARKER:
        if ord(recieve_char) != START_MARKER:
            recieve_string = recieve_string + recieve_char
        recieve_char = SERIAL_OBJECT[port].read()
        recieve_char = recieve_char.decode("utf-8")
    return recieve_string


def run(parce_string, port):
    """Wait until the Arduino sends "Arduino Ready" - allows time for Arduino
    reset it also ensures that any bytes left over from a previous message are
    discarded"""
    try:
        run_execute(parce_string, port)
    except timeout_decorator.TimeoutError:
        SPINNER.write(
            "== == Array: "
            + str(port)
            + " \033[31m"
            + "EXECUTION FAILED TIMEOUT"
            + "\033[0m"
        )


@timeout_decorator.timeout(100, use_signals=False)
def run_execute(parce_string, port):
    """Sends commands Arduino and then waits for a reply. Created off run() so
    we can have both a timeout and a try catch block"""
    waiting_for_reply = False
    if not waiting_for_reply:
        SERIAL_OBJECT[port].write(parce_string.encode())
        SPINNER.write("-> -> Array: " + str(port) + " \033[32m" + "SENT" + "\033[0m")
        waiting_for_reply = True

    if waiting_for_reply:
        while SERIAL_OBJECT[port].inWaiting() == 0:
            pass
        data_recieved = recieve_from_arduino(port)
        SPINNER.write("<- <- Array: " + str(port) + " " + data_recieved)
        waiting_for_reply = False


def csv_commands():
    """Reads data from desiered_state.csv, lints it, and then executes the
    commands"""
    # lint desired_state csv values and make sure that they are in range
    desired_state_list = []
    with open("desired_state.csv", "r") as desired_state_file:
        desired_state_reader = csv.reader(desired_state_file, delimiter=",")
        desired_state_list = list(desired_state_reader)
    for count_row, row in enumerate(desired_state_list):
        for count_column, column in enumerate(row):
            if int(column) > MAX_TURNS:
                desired_state_list[count_row][count_column] = str(MAX_TURNS)
            elif int(column) < 0:
                desired_state_list[count_row][count_column] = "0"
    with open("desired_state.csv", "w", newline="") as desired_state_file:
        desired_state_writer = csv.writer(desired_state_file, quoting=csv.QUOTE_ALL)
        desired_state_writer.writerows(desired_state_list)

    # fill command string
    command_string = ""
    desired_state_list = []
    current_state_list = []
    with open("desired_state.csv", "r") as desired_state_file:
        desired_state_reader = csv.reader(desired_state_file, delimiter=",")
        desired_state_list = list(desired_state_reader)
    with open("current_state.csv", "r", newline="") as current_state_file:
        current_state_reader = csv.reader(current_state_file, delimiter=",")
        current_state_list = list(current_state_reader)
    # assumption here is that both csvs are the size
    for count_row, row in enumerate(desired_state_list):
        command_string += "<"
        for count_column, column in enumerate(row):
            difference = int(current_state_list[count_row][count_column]) - int(
                desired_state_list[count_row][count_column]
            )
            if difference < 0:
                command_string += "Down,"
            elif difference > 0:
                command_string += "Up,"
            else:
                command_string += "None,"
            command_string += str(abs(difference)) + ","
        command_string = command_string[:-1]
        command_string += ">;"
    # remove final semicolon
    command_string = command_string[:-1]
    # call execute commands
    execute_commands(command_string)
    # update current_state.csv with the values of desired_state.csv
    shutil.copy2('desired_state.csv', "current_state.csv")


def reset_commands():
    """Preforms a reset on the ceiling """
    current_state_list = []
    command_string = ""
    with open("current_state.csv", "r") as current_state_file:
        current_state_reader = csv.reader(current_state_file, delimiter=",")
        current_state_list = list(current_state_reader)
    for count_row, row in enumerate(current_state_list):
        command_string += "<"
        for count_column, _ in enumerate(row):
            current_state_list[count_row][count_column] = "0"
            command_string += "Up,100,"
        command_string = command_string[:-1]
        command_string += ">;"
    command_string = command_string[:-1]
    with open("current_state.csv", "w", newline="") as current_state_file:
        current_state_writer = csv.writer(current_state_file, quoting=csv.QUOTE_ALL)
        current_state_writer.writerows(current_state_list)
    # call execute commands
    execute_commands(command_string)


def execute_commands(command_string_execute):
    """ Creates threads that send commands to the Arduinos and wait for replies.
    there is one thread for each Arduino"""
    parse_text = command_string_execute.split(";")
    threads = [None] * NUMBER_OF_ARRAYS
    SPINNER.start()
    # create threads
    for count, _ in enumerate(parse_text):
        threads[count] = Thread(target=run, args=(parse_text[count], count))
    # start threads
    for count, _ in enumerate(parse_text):
        threads[count].start()
    # wait for threads to finish
    for count, _ in enumerate(parse_text):
        threads[count].join()
    SPINNER.stop()


def close_connections():
    """ Closes serial ports"""
    print("\nClosing Ports")
    SPINNER.start()
    for count, _ in enumerate(SERIAL_PORT):
        try:
            SERIAL_OBJECT[count].close
            SPINNER.write(
                "Serial port "
                + str(count)
                + " "
                + SERIAL_PORT[count]
                + " \033[32m"
                + "CLOSED"
                + "\033[0m"
            )
        except AttributeError:
            SPINNER.write(
                "Serial port "
                + str(count)
                + " "
                + SERIAL_PORT[count]
                + " \033[31m"
                + "FAILED"
                + "\033[0m"
            )
            SPINNER.stop()
    SPINNER.stop()


def main():
    """ Main function of the program. Also provides tui in terminal to interact with
    """
    global DID_ERROR_OCCUR
    global SERIAL_OBJECT
    while True:
        DID_ERROR_OCCUR = False
        input_text_1 = input("\n\nPress Enter to Start the Program or type 'Exit' to Close:")
        if input_text_1 in ('Exit', 'exit'):
            break
        print("\nOpening Ports")
        SPINNER.start()

        for count, _ in enumerate(SERIAL_PORT):
            try:
                SERIAL_OBJECT[count] = serial.Serial(SERIAL_PORT[count], BAUD_RATE)
                SPINNER.write(
                    "Serial Port "
                    + str(count)
                    + " "
                    + SERIAL_PORT[count]
                    + " \033[32m"
                    + "READY"
                    + "\033[0m"
                )
            except serial.serialutil.SerialException:
                SPINNER.write(
                    "Serial Port "
                    + str(count)
                    + " "
                    + SERIAL_PORT[count]
                    + " \033[31m"
                    + "FAILED"
                    + "\033[0m"
                )
                SPINNER.stop()
                DID_ERROR_OCCUR = True
        SPINNER.stop()

        if not DID_ERROR_OCCUR:
            print("\nChecking for CSV Files")
            if path.exists("current_state.csv"):
                print("current_state CSV: \033[32m FOUND\033[0m")
            else:
                print("current_state CSV: \033[31m NOT FOUND\033[0m")
                DID_ERROR_OCCUR = True
            if path.exists("desired_state.csv"):
                print("desired_state CSV: \033[32m FOUND\033[0m")
            else:
                print("desired_state CSV: \033[31m NOT FOUND\033[0m")
                DID_ERROR_OCCUR = True

        if not DID_ERROR_OCCUR:
            print("\nConnecing to Arrays")
            connecting_threads = [None] * NUMBER_OF_ARRAYS
            SPINNER.start()
            # create threads
            for count, _ in enumerate(SERIAL_PORT):
                connecting_threads[count] = Thread(target=wait_for_arduino, args=[count])

            # start threads
            for count, _ in enumerate(SERIAL_PORT):
                connecting_threads[count].start()

            # wait for threads to finish
            for count, _ in enumerate(SERIAL_PORT):
                connecting_threads[count].join()
            SPINNER.stop()

        if not DID_ERROR_OCCUR:
            break

        close_connections()


    while input_text_1 not in ('Exit', 'exit'):
        print("===========\n")
        input_text_2 = input(
            "Enter '1' to set ceiling from csv, '2' to reset, and 'Exit' to close program)\n : "
        )
        # csv mode
        if input_text_2 == "1":
            print("CSV Mode\n")
            csv_commands()
        # csv reset
        elif input_text_2 == "2":
            print("CSV Reset Mode\n")
            reset_commands()
        # manual mode
        elif input_text_2 == "3":
            print("Manual Mode\n")
            execute_commands(input("Enter Commands (format '<Up,1>;<Up,1>'):\n : "))
        # exit
        elif input_text_2 in ("Exit", "exit"):
            # close all serial connections
            close_connections()
            break
        else:
            print("Invalid Input\n")

# global variables
NUMBER_OF_ARRAYS = 2
SERIAL_PORT = ["/dev/ttyUSB0", "/dev/ttyUSB1"]
MAX_TURNS = 10
BAUD_RATE = 9600
START_MARKER = 60
END_MARKER = 62
SPINNER = yaspin(Spinners.weather)
# global serial object
SERIAL_OBJECT = [None] * NUMBER_OF_ARRAYS
# need this for error checking in threads
DID_ERROR_OCCUR = False


if __name__ == "__main__":
    main()
