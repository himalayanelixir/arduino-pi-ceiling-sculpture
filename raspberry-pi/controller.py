#!/home/pi/code/pi_env/bin/python3
# Copyright 2020 Harlen Bains
# linted using pylint
# formatted using black
"""This script runs on the Raspberry Pi and sends commands to Arduinos.
Once a command is sent it then waits a reply and then loops.
"""

import csv
import shutil
import subprocess
import time
import glob
import os
from os import path
from threading import Thread
import serial  # pylint: disable=import-error
from yaspin import yaspin  # pylint: disable=import-error
from yaspin.spinners import Spinners  # pylint: disable=import-error
import timeout_decorator  # pylint: disable=import-error
import questionary  # pylint: disable=import-error


# constants
# don't change
BAUD_RATE = 9600
START_MARKER = 60
END_MARKER = 62
SPINNER = yaspin(Spinners.weather)
# adjustable
# positive integers only
MAX_TURNS = 10
MAX_NUMBER_OF_ARRAYS = 5
MAX_NUMBER_OF_MOTORS = 10
USB_PATH = "/dev/ttyU*"
CSV_PATH = "/home/pi/"
CURRENT_STATE_FILENAME = "/home/pi/code/current-state.csv"


class Error(Exception):
    """Exception that is raised when an error occurs in the program
    causes the program to print out a message and then loop.
    """


def find_arduinos():
    """Run ls command and find all USB devices connected to USB hub
     assume that all of them are Arduinos.

    Returns:
      A list of all the ports that are active on the USB hub.

    Raises:
      Error: if no arrays are found or if more than MAX_NUMBER_OF_ARRAYS is
    found.
    """
    # run ls in subprocess shell and save results
    try:
        path_command = "ls " + USB_PATH
        serial_shell_capture = subprocess.run(
            [path_command], shell=True, capture_output=True, check=True
        )
        # take results and convert byte string into utf-8 and create list based on newlines
        serial_shell_capture_list = serial_shell_capture.stdout.decode(
            "utf-8"
        ).splitlines()
        # if there is at least one array found then print out number found
        # other wise print zero and error
        print(
            f"Found \033[32m{len(serial_shell_capture_list)}\033[0m Array(s)",
            f"of Max of {MAX_NUMBER_OF_ARRAYS}",
        )
        # make sure that the # arrays found is less than or equal to MAX_NUMBER_OF_ARRAYS
        if len(serial_shell_capture_list) > MAX_NUMBER_OF_ARRAYS:
            # make list empty so we don't try to close ports when this error occurs
            serial_shell_capture_list = []
            print(
                f"\033[31mERROR: NUMBER OF ARRAYS FOUND GREATER THAN {MAX_NUMBER_OF_ARRAYS}\033[0m"
            )
            raise Error
    except subprocess.CalledProcessError:
        # need to still have a valie
        serial_shell_capture_list = []
        print(f"\nFound \033[31m0\033[0m Array(s) of Max {MAX_NUMBER_OF_ARRAYS}")
        print(
            f"\033[31mERROR: NO ARRAYS FOUND\033[0m"
        )
        raise Error
    return serial_shell_capture_list


def check_csv(filename):
    """Runs functions that check for and lint csv files.
    """
    # check if the csvs for desired and current state exist
    print("Checking for CSV Files")
    check_if_csv_exists(filename)
    # lint csvs so that the contain valid data and are the correct size
    lint_csv_file(filename)


def check_if_csv_exists(csv_filename):
    """Check if file exists.

    Args:
      csv_filename: The name of the file we are checking for.

    Raises:
      Error: If file is not found.
    """
    if path.exists(csv_filename):
        print(csv_filename + " (\033[32mFOUND\033[0m)")
    else:
        print(csv_filename + " (\033[31mERROR: FILE NOT FOUND\033[0m)")
        raise Error


def lint_csv_file(csv_filename):
    """Lint file table is the corret size and values are valid.

    Args:
      csv_filename: The name of the file we are linting.

    Raises:
      Error: If the program can not read the file.
      Error: If the program can not write to the file.
    """
    csv_filename_list = []
    # we initialize this list to a particular size becuase we then iterate over it and
    # copy values from csv_filename_list. When copying we also make sure that the
    # values are allowed (filters out non ints and values that are too high or low)
    csv_filename_list_linted = [
        ["0" for x in range(MAX_NUMBER_OF_MOTORS)] for y in range(MAX_NUMBER_OF_ARRAYS)
    ]
    try:
        with open(csv_filename, "r") as csv_filename_file:
            csv_filename_reader = csv.reader(csv_filename_file, delimiter=",")
            csv_filename_list = list(csv_filename_reader)
            for count_row in range(0, MAX_NUMBER_OF_ARRAYS):
                for count_column in range(0, MAX_NUMBER_OF_MOTORS):
                    try:
                        # pylint: disable=C0330
                        if (
                            int(csv_filename_list[count_row][count_column]) <= MAX_TURNS
                            and int(csv_filename_list[count_row][count_column]) > 0
                            and csv_filename_list[count_row][count_column] != ""
                            and isinstance(
                                int(csv_filename_list[count_row][count_column]), int
                            )
                        ):
                            csv_filename_list_linted[count_row][
                                count_column
                            ] = csv_filename_list[count_row][count_column]
                        else:
                            csv_filename_list_linted[count_row][count_column] = "0"
                    except (IndexError, ValueError):
                        csv_filename_list_linted[count_row][count_column] = "0"
    except EnvironmentError:
        SPINNER.write(
            csv_filename + " (\033[31m" + "ERROR: CAN'T READ CSV" + "\033[0m)"
        )
        raise Error
    # write values to file overwriting previous file
    try:
        with open(csv_filename, "w", newline="") as csv_filename_file:
            csv_filename_writer = csv.writer(csv_filename_file, quoting=csv.QUOTE_ALL)
            csv_filename_writer.writerows(csv_filename_list_linted)
            SPINNER.write(csv_filename + " (\033[32m" + "LINTED" + "\033[0m)")
    except EnvironmentError:
        SPINNER.write(
            csv_filename + " (\033[31m" + "ERROR: CAN'T WRITE CSV" + "\033[0m)"
        )
        raise Error


def lint_serial_port_values(serial_ports):
    """Makes sure that the numbers for array number and number of motors is valid.

    Args:
      serial_ports: List containing address of USB ports, pySerial object, array number,
        and number of motors.

    Raises:
      Error: Duplicate array numbers
      Error: Number of array is out of range or too many are connected.
      Error: Number of motors is out or range.
    """
    error = False
    list_array_numbers = []
    list_motor_numbers = []
    seen = {}
    duplicates = []
    print("\nChecking Array and Motor Numbers")
    for row in serial_ports:
        list_array_numbers.append(row[2])
        list_motor_numbers.append(row[3])
    # check if there are any duplicates
    for number in list_array_numbers:
        if number not in seen:
            seen[number] = 1
        else:
            if seen[number] == 1:
                duplicates.append(number)
            seen[number] += 1
    for number in duplicates:
        print(f"Array Numbers (\033[31mERROR: ARRAY {number} DUPLICATES\033[0m)")
        error = True
    # check and see if any of the arrays are out of the correct range
    for number in list_array_numbers:
        # >= because array numbers from the Arduino start at 0
        if int(number) >= MAX_NUMBER_OF_ARRAYS or int(number) < 0:
            print(f"Array Numbers (\033[31mERROR: ARRAY {number} OUT OF RANGE\033[0m)")
            error = True
    # check and see if any of the motor numbers are out of the correct range
    for count_number, number in enumerate(list_motor_numbers):
        # > because motor numbers start at 1 when counted aka 0 motors means no motors
        # while 1 motor means #0. When sending commands motor one is considered as #0
        if int(number) > MAX_NUMBER_OF_MOTORS or int(number) < 1:
            print(
                f"Motor Numbers (\033[31mERROR: ARRAY {list_array_numbers[count_number]}",
                "NUMBER OF MOTORS {number} OUT OF RANGE\033[0m)",
            )
            error = True
    if error:
        raise Error
    print("Array Numbers (\033[32mCOMPLETE\033[0m)")
    print("Motor Numbers (\033[32mCOMPLETE\033[0m)")


def commands_from_csv(serial_ports, desired_state_filename):
    """Reads data from desiered_state.csv, lints it, and then executes the commands.

    Args:
      serial_ports: List containing address of USB ports, pySerial object, array number,
        and number of motors.
    """
    # fill command string
    command_string = ""
    desired_state_list = []
    current_state_list = []
    # not putting try except blocks around with statements because they have
    # already been read and written to before and are accessable
    with open(desired_state_filename, "r") as desired_state_file:
        desired_state_reader = csv.reader(desired_state_file, delimiter=",")
        desired_state_list = list(desired_state_reader)
    with open(CURRENT_STATE_FILENAME, "r", newline="") as current_state_file:
        current_state_reader = csv.reader(current_state_file, delimiter=",")
        current_state_list = list(current_state_reader)
    for count_row, _ in enumerate(serial_ports):
        # beginning of every command for an array
        command_string += "<"
        # get desired state row correspnding to the array number
        desired_row = desired_state_list[serial_ports[count_row][2]]
        # get current state row correspnding to the array number
        current_row = current_state_list[serial_ports[count_row][2]]
        for count_column, _ in enumerate(desired_row):
            # < because motor number isn't counting from zero
            if count_column < serial_ports[count_row][3]:
                difference = int(current_row[count_column]) - int(
                    desired_row[count_column]
                )
                if difference < 0:
                    command_string += "Down,"
                elif difference > 0:
                    command_string += "Up,"
                else:
                    command_string += "None,"
                # make sure that the number of turns is positive
                command_string += str(abs(difference)) + ","
        # remove extra comma
        command_string = command_string[:-1]
        command_string += ">;"
    # remove final semicolon
    command_string = command_string[:-1]
    # call execute commands
    print(command_string)
    execute_commands(serial_ports, command_string)
    shutil.copy2(desired_state_filename, CURRENT_STATE_FILENAME)


def commands_from_variable(serial_ports, variable_string):
    """Sends the same command to every motor in the ceiling. Used for reset and testing.

    Args:
      serial_ports: List containing address of USB ports, pySerial object, array number,
        and number of motors.
      variable_string: Command that we want every motor to execute. Example: "Up,100,".
    """
    command_string = ""
    # first we zero the current state file
    current_state_list_zero = [
        ["0" for x in range(MAX_NUMBER_OF_ARRAYS)] for y in range(MAX_NUMBER_OF_MOTORS)
    ]
    with open(CURRENT_STATE_FILENAME, "w", newline="") as current_state_file:
        current_state_writer = csv.writer(current_state_file, quoting=csv.QUOTE_ALL)
        current_state_writer.writerows(current_state_list_zero)

    for count_row, _ in enumerate(serial_ports):
        # beginning of every command for an array
        command_string += "<"
        for _ in range(serial_ports[count_row][3]):
            command_string += variable_string
        # remove extra comma
        command_string = command_string[:-1]
        command_string += ">;"
    # remove final semicolon
    command_string = command_string[:-1]
    # call execute commands
    print(command_string)
    execute_commands(serial_ports, command_string)


def execute_commands(serial_ports, command_string_execute):
    """Creates threads that send commands to the Arduinos and wait for replies.
    there is one thread for each Arduino.

    Args:
      serial_ports: List containing address of USB ports, pySerial object, array number,
        and number of motors.
      command_string_execute: String of commands that are to be sent to all the arrays.
    """
    parse_text = command_string_execute.split(";")
    threads = [None] * len(serial_ports)
    SPINNER.start()
    # create threads
    for count, _ in enumerate(parse_text):
        threads[count] = Thread(
            target=move_arrays, args=(serial_ports, parse_text[count], count)
        )
        # start threads
        threads[count].start()
    # wait for threads to finish
    for count, _ in enumerate(parse_text):
        threads[count].join()
    SPINNER.stop()


def open_ports(serial_ports):
    """Open ports and create pySerial objects saving them to serial_ports.

    Args:
      serial_ports: List containing address of USB ports, pySerial object, array number,
        and number of motors.

    Returns:
      Returns a list with serial_ports data but with the pySerial object added for each array.

    Raises:
      Error: If pySerial object cannot be created.
    """
    print("\nOpening Port(s)")
    SPINNER.start()
    # go through serial_ports list and try to connect to usb devices
    # otherwise error
    for count, _ in enumerate(serial_ports):
        try:
            serial_ports[count] = [
                serial_ports[count],
                serial.Serial(serial_ports[count], BAUD_RATE),
            ]
            SPINNER.write(
                "Serial Port "
                + str(count)
                + " "
                + serial_ports[count][0]
                + " (\033[32m"
                + "COMPLETE"
                + "\033[0m)"
            )
        except serial.serialutil.SerialException:
            SPINNER.write(
                "Serial Port "
                + str(count)
                + " "
                + serial_ports[count][0]
                + " (\033[31m"
                + "ERROR"
                + "\033[0m)"
            )
            SPINNER.stop()
            raise Error
    SPINNER.stop()
    return serial_ports


def connect_to_arrays(serial_ports):
    """Connect to arrays and retrieve connection message.

    Args:
      serial_ports: List containing address of USB ports, pySerial object, array number,
        and number of motors.

    Returns:
      Returns a list with serial_ports data but with array number and number of motors
        filled in for each array.

    Raises:
      Error: If the correct message is not recived within timeout.
    """
    print("\nConnecting to Array(s)")
    # used for thread objects
    connection_threads = [None] * len(serial_ports)
    # used to store returned values from threads
    results = [None] * len(serial_ports)
    SPINNER.start()
    # create threads
    for count, _ in enumerate(serial_ports):
        connection_threads[count] = Thread(
            target=wait_for_arduino_connection, args=(serial_ports, count, results)
        )
        # start threads
        connection_threads[count].start()
    # wait for threads to finish
    for count, _ in enumerate(serial_ports):
        connection_threads[count].join()
    SPINNER.stop()
    # get returned values from threads and assign to serial_port
    for count_row, row in enumerate(results):
        if row[0]:
            raise Error
        serial_ports[count_row] = row[1]
    return serial_ports


def wait_for_arduino_connection(serial_ports, port, results):
    """Wait until the Arduino sends "Arduino is Ready" - allows time for Arduino
    reset it also ensures that any bytes left over from a previous message are
    discarded.

    Args:
      serial_ports: List containing address of USB ports, pySerial object, array number,
        and number of motors.
      port: Thread number created from enumerating through serial_ports.
      results: Used to find if errors occoured in the thread and pass back to connect_to_arrays().
    """
    error = False
    try:
        array_info = wait_for_arduino_connection_execute(serial_ports, port)
        serial_ports[port] = [
            serial_ports[port][0],
            serial_ports[port][1],
            array_info[0],
            array_info[1],
        ]
        SPINNER.write(
            "Serial Port "
            + str(port)
            + " ARRAY "
            + str(array_info[0])
            + " MOTOR(S) "
            + str(array_info[1])
            + " (\033[32mCOMPLETE\033[0m)"
        )
    except timeout_decorator.TimeoutError:
        error = True
        SPINNER.write(
            "Serial Port "
            + str(port)
            + " (\033[31m"
            + "ERROR: WAITING FOR MESSAGE TIMEOUT"
            + "\033[0m)"
        )
    except IndexError:
        error = True
        SPINNER.write(
            "Serial Port "
            + str(port)
            + " (\033[31m"
            + "ERROR: NEGATIVE ARRAY NUMBER OR MOTOR NUMBER PASSED"
            + "\033[0m)"
        )
    # works as a return functon for the thread
    results[port] = [error, serial_ports[port]]


@timeout_decorator.timeout(10, use_signals=False)
def wait_for_arduino_connection_execute(serial_ports, port):
    """Waits for Arduino to send ready message. Created so we can have a
    timeout and a try catch block.

    Args:
      serial_ports: List containing address of USB ports, pySerial object, array number,
        and number of motors.
      port: Thread number created from enumerating through serial_ports.

    Returns:
      Array number and the number of motors conntected to it.
    """
    msg = ""
    while msg.find("Arduino is Ready") == -1:
        while serial_ports[port][1].inWaiting() == 0:
            pass
        msg = recieve_from_arduino(serial_ports, port)
    # gets the array number and the number of motors in the array
    array_info = [int(i) for i in msg.split() if i.isdigit()]
    return array_info


def recieve_from_arduino(serial_ports, port):
    """Gets message from Arduino.

    Args:
      serial_ports: List containing address of USB ports, pySerial object, array number,
        and number of motors.
      port: Thread number created from enumerating through serial_ports.

    Returns:
      The string that was returned from the Arduino.
    """
    recieve_string = ""
    # any value that is not an end- or START_MARKER
    recieve_char = "z"
    recieve_char = serial_ports[port][1].read()
    recieve_char = recieve_char.decode("utf-8")
    # wait for the start character
    while ord(recieve_char) != START_MARKER:
        recieve_char = serial_ports[port][1].read()
        recieve_char = recieve_char.decode("utf-8")
    # save data until the end marker is found
    while True:
        recieve_char = serial_ports[port][1].read()
        recieve_char = recieve_char.decode("utf-8")
        if ord(recieve_char) == END_MARKER:
            break
        recieve_string = recieve_string + recieve_char
    return recieve_string


def move_arrays(serial_ports, parce_string, port):
    """Wait until the Arduino sends "Arduino Ready" - allows time for Arduino
    reset it also ensures that any bytes left over from a previous message are
    discarded.

    Args:
      serial_ports: List containing address of USB ports, pySerial object, array number,
        and number of motors.
      parce_string: String of commands sent to an array
      port: Thread number created from enumerating through serial_ports.
    """
    try:
        move_arrays_execute(serial_ports, parce_string, port)
    except timeout_decorator.TimeoutError:
        SPINNER.write(
            "== == Array: "
            + str(port)
            + " (\033[31m"
            + "EXECUTION ERROR TIMEOUT"
            + "\033[0m)"
        )


@timeout_decorator.timeout(100, use_signals=False)
def move_arrays_execute(serial_ports, parce_string, port):
    """Sends commands Arduino and then waits for a reply. Created off move_arrays() so
    we can have both a timeout and a try catch block.

    Args:
      serial_ports: List containing address of USB ports, pySerial object, array number,
        and number of motors.
      parce_string: String of commands sent to an array
      port: Thread number created from enumerating through serial_ports.
    """
    waiting_for_reply = False
    if not waiting_for_reply:
        serial_ports[port][1].write(parce_string.encode())
        SPINNER.write("-> -> Array: " + str(port) + " (\033[32m" + "SENT" + "\033[0m)")
        waiting_for_reply = True

    if waiting_for_reply:
        while serial_ports[port][1].inWaiting() == 0:
            pass
        data_recieved = recieve_from_arduino(serial_ports, port)
        SPINNER.write("<- <- Array: " + str(port) + " (" + data_recieved + ")")
        waiting_for_reply = False


def close_connections(serial_ports):
    """Closes serial port(s)

    Args:
      serial_ports: List containing address of USB ports, pySerial object, array number,
        and number of motors.
    """
    print("\nClosing Port(s)")
    SPINNER.start()
    for count, _ in enumerate(serial_ports):
        try:
            serial_ports[count][1] = serial_ports[count][1].close
            SPINNER.write(
                "Serial port "
                + str(count)
                + " "
                + serial_ports[count][0]
                + " (\033[32m"
                + "CLOSED"
                + "\033[0m)"
            )
        except AttributeError:
            SPINNER.write(
                "Serial port "
                + str(count)
                + " "
                + serial_ports[count][0]
                + " (\033[31m"
                + "ERROR"
                + "\033[0m)"
            )
            SPINNER.stop()
    SPINNER.stop()


def find_csvs():
    """Finds csv files in CSV_PATH. Used to populate menu.

    Returns:
      List contatining strings with the names of the csv files in CSV_PATH.
    """
    os.chdir(CSV_PATH)
    csvs_found = glob.glob("*.{}".format("csv"))
    if not csvs_found:
        csvs_found = ["No csv's found"]
    return csvs_found


def main():
    """Loop of the program. Provides tui to interact with the ceiling sculpture
    """
    # address of USB port,pySerial object, array number, and number of motors
    serial_ports = []
    while True:
        try:
            print(
                """\033[35m                       __                __ __           """
            )  # pylint: disable=anomalous-backslash-in-string
            print(
                """  _____ ____   ____   / /_ _____ ____   / // /___   _____"""
            )  # pylint: disable=anomalous-backslash-in-string
            print(
                """ / ___// __ \ / __ \ / __// ___// __ \ / // // _ \ / ___/"""
            )  # pylint: disable=anomalous-backslash-in-string
            print(
                """/ /__ / /_/ // / / // /_ / /   / /_/ // // //  __// /    """
            )  # pylint: disable=anomalous-backslash-in-string
            print(
                """\___/ \____//_/ /_/ \__//_/    \____//_//_/ \___//_/     \033[0m"""
            )  # pylint: disable=anomalous-backslash-in-string
            print(
                f"\033[96mMAX TURNS {MAX_TURNS} -- MAX ARRAYS {MAX_NUMBER_OF_ARRAYS}",
                f" -- MAX MOTORS {MAX_NUMBER_OF_MOTORS}\nUSB PATH {USB_PATH}",
                f" -- CSV PATH {CSV_PATH}\033[0m\n",
            )
            # wait for user to want to run program
            input_text_1 = questionary.select(
                "What do you want to do?", choices=["Start", "Exit"]
            ).ask()
            if input_text_1 == "Exit":
                break
            # find all usb devices connected at /dev/ttyU*
            # we are assuming that all usb devices at this address are Arduinos
            serial_ports = find_arduinos()
            # initialize serial_objecs size based on the number of Arduinos
            # open ports at address /dev/ttyU* that we found earlier
            serial_ports = open_ports(serial_ports)
            # connect to the arrays and then save the array number and number of motors
            serial_ports = connect_to_arrays(serial_ports)
            # lint the data we recieved from the arrays
            lint_serial_port_values(serial_ports)
            # if error didn't occour exit this loop and move on to the next one
            break
        except Error:
            # if we got to connecting to ports then close ports otherwise loop
            if len(serial_ports) != 0:
                close_connections(serial_ports)
    ###########
    while input_text_1 not in ("Exit", "exit"):
        try:
            print("\033[96m===========\033[0m\n")
            input_text_2 = questionary.select(
                "What do you want to do?",
                choices=["Run from csv", "Reset", "Test", "Exit"],
            ).ask()
            if input_text_2 == "Run from csv":
                input_text_3 = questionary.select(
                    "Which csv file do you want to use?", find_csvs()
                ).ask()
                check_csv(input_text_3)
                check_csv(CURRENT_STATE_FILENAME)
                commands_from_csv(serial_ports, input_text_3)
            elif input_text_2 == "Reset":
                check_csv(CURRENT_STATE_FILENAME)
                commands_from_variable(serial_ports, "Up,100,")
            elif input_text_2 == "Test":
                print("\nTest Mode (Only way to stop is to 'ctrl + c')\n")
                while True:
                    print("Resetting\n")
                    commands_from_variable(serial_ports, "Up,100,")
                    print("Wait 10 seconds\n")
                    time.sleep(10)
                    print("Moving Down 5 Turns\n")
                    commands_from_variable(serial_ports, "Down,5,")
                    print("Wait 10 seconds\n")
                    time.sleep(10)
            elif input_text_2 == "Exit":
                close_connections(serial_ports)
                break
        except Error:
            pass


if __name__ == "__main__":
    main()
