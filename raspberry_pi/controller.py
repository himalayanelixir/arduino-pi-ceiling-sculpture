#!/home/pi/controller_env/bin/python3
"""This script runs on the Raspberry Pi and sends commands to Arduinos.
Once a command is sent it then waits a reply
"""

import csv
import shutil
import subprocess
from os import path
from threading import Thread
import serial
from yaspin import yaspin
from yaspin.spinners import Spinners
import timeout_decorator


def find_arduinos():
    """Run ls command and find all USB devices connected to USB hub
     assume that all of them are arduinos"""
    error = False
    # run ls in subprocess shell and save results
    serial_shell_capture = subprocess.run(
        ["ls /dev/ttyU*"], shell=True, capture_output=True, check=True
    )
    # take results and convert byte string into utf-8 and create list based on newlines
    serial_shell_capture_list = serial_shell_capture.stdout.decode("utf-8").splitlines()
    # if there is at least one array found then print out number found
    # other wise print zero and error
    if len(serial_shell_capture_list) != 0:
        print(f"\nFound \033[32m{len(serial_shell_capture_list)}\033[0m Array(s)")
    else:
        print(f"\nFound \033[31m{len(serial_shell_capture_list)}\033[0m Arrays")
        error = True
    return error, serial_shell_capture_list


def check_if_csvs_exist(csv_filename):
    """Check if csvs for desired state and current state exist"""
    error = False
    if path.exists(csv_filename):
        print(csv_filename + "\033[32m FOUND\033[0m")
    else:
        print(csv_filename + "current_state CSV\033[31m NOT FOUND\033[0m")
        error = True
    return error


def lint_csv_files(csv_filename):
    """Lint csv_filename csv values and make sure that they are in range also make
    sure that csv is the right size and the values are valid"""
    error = False
    csv_filename_list = []
    # we initialize this list to a particular size becuase we then iterate over it and
    # copy values from csv_filename_list. When copying we also make sure that the
    # values are allowed (filters out non ints and values that are too high or low)
    csv_filename_list_linted = [
        ["0" for x in range(MAX_NUMBER_OF_ARRAYS)] for y in range(MAX_NUMBER_OF_MOTORS)
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
                            and int(csv_filename_list[count_row][count_column]) >= 0
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
        error = True
        SPINNER.write(csv_filename + " \033[31m" + "LINTING FAILED: READ CSV" + "\033[0m")
    # write values to file overwriting previous file
    try:
        with open(csv_filename, "w", newline="") as csv_filename_file:
            csv_filename_writer = csv.writer(csv_filename_file, quoting=csv.QUOTE_ALL)
            csv_filename_writer.writerows(csv_filename_list_linted)
            SPINNER.write(csv_filename + " \033[32m" + "LINTED" + "\033[0m")
    except EnvironmentError:
        error = True
        SPINNER.write(csv_filename + " \033[31m" + "LINTING FAILED: WRITE CSV" + "\033[0m")

    return error


def lint_serial_port_values(serial_ports):
    """Makes sure that the values for array number and number of motors is valid"""
    error = False
    list_array_numbers = []
    list_motor_numbers = []
    print("\nChecking Array and Motor Values")
    for row in serial_ports:
        list_array_numbers.append(row[2])
        list_motor_numbers.append(row[3])
    # check if there are any duplicates
    if len(list_array_numbers) != len(set(list_array_numbers)):
        error = True
        print("Array Values \033[31mLINTING FAILED: DUPLICATES\033[0m")
    # check and see if any of the arrays are out of the correct range
    for value in list_array_numbers:
        if int(value) > MAX_NUMBER_OF_ARRAYS or int(value) < 0:
            error = True
            print("Array Values \033[31mLINTING FAILED: OUT OF RANGE\033[0m")
    # check and see if any of the motor numbers are out of the correct range
    for value in list_motor_numbers:
        if int(value) > MAX_NUMBER_OF_MOTORS or int(value) < 1:
            error = True
            print("Motor Values \033[31mLINTING FAILED: OUT OF RANGE\033[0m")

    if not error:
        print("Array Values \033[32mLINTED\033[0m")
        print("Motor Values \033[32mLINTED\033[0m")
    return error


def commands_from_csv(serial_ports):
    """Reads data from desiered_state.csv, lints it, and then executes the
    commands"""
    # fill command string
    command_string = ""
    desired_state_list = []
    current_state_list = []
    # not putting try except blocks around with statements because they have
    # already been read and written to before and are accessable
    with open(DESIRED_STATE_FILENAME, "r") as desired_state_file:
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
    # shutil.copy2(DESIRED_STATE_FILENAME, CURRENT_STATE_FILENAME)


def commands_from_reset(serial_ports):
    """Preforms a reset on the ceiling """
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
            command_string += "Up,100,"
        # remove extra comma
        command_string = command_string[:-1]
        command_string += ">;"
    # remove final semicolon
    command_string = command_string[:-1]
    # call execute commands
    print(command_string)
    execute_commands(serial_ports, command_string)


def execute_commands(serial_ports, command_string_execute):
    """ Creates threads that send commands to the Arduinos and wait for replies.
    there is one thread for each Arduino"""
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


##############################################################################
##############################################################################
##############################################################################
def open_ports(serial_ports):
    """Open ports and create pyserial objects saving them to serial_ports"""
    print("\nOpening Port(s)")
    error = False
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
                + " \033[32m"
                + "READY"
                + "\033[0m"
            )
        except serial.serialutil.SerialException:
            SPINNER.write(
                "Serial Port "
                + str(count)
                + " "
                + serial_ports[count][0]
                + " \033[31m"
                + "FAILED"
                + "\033[0m"
            )
            SPINNER.stop()
            error = True
    SPINNER.stop()
    return error, serial_ports


def connect_to_arrays(serial_ports):
    """Connect to arrays and retrieve connection message"""
    print("\nConnecing to Arrays")
    error = False
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
            error = True
        serial_ports[count_row] = row[1]
    return error, serial_ports


def wait_for_arduino_connection(serial_ports, port, results):
    """Wait until the Arduino sends "Arduino Ready" - allows time for Arduino
    reset it also ensures that any bytes left over from a previous message are
    discarded """
    # we had to create seperate functions wait_for_arduino_connection and
    # wait_for_arduino_connection_execute because I wanted to add a timer to the execution
    # this way we can timeout connections
    error = False
    try:
        array_info = wait_for_arduino_connection_execute(serial_ports, port)
        serial_ports[port] = [
            serial_ports[port][0],
            serial_ports[port][1],
            array_info[0],
            array_info[1],
        ]
        SPINNER.write("Serial Port " + str(port) + " \033[32m" + "READY" + "\033[0m")
    except timeout_decorator.TimeoutError:
        SPINNER.write("Serial Port " + str(port) + " \033[31m" + "FAILED" + "\033[0m")
        error = True
    # works as a return functon for the thread
    results[port] = [error, serial_ports[port]]


@timeout_decorator.timeout(10, use_signals=False)
def wait_for_arduino_connection_execute(serial_ports, port):
    """ Waits for Arduino to send ready message. Created so we can have a
    timeout and a try catch block"""

    msg = ""
    while msg.find("Arduino is ready") == -1:
        while serial_ports[port][1].inWaiting() == 0:
            pass
        msg = recieve_from_arduino(serial_ports, port)
    # gets the array number and the number of motors in the array
    array_info = [int(i) for i in msg.split() if i.isdigit()]
    return array_info


def recieve_from_arduino(serial_ports, port):
    """ Gets message from Arduino"""
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
    while ord(recieve_char) != END_MARKER:
        if ord(recieve_char) != START_MARKER:
            recieve_string = recieve_string + recieve_char
        recieve_char = serial_ports[port][1].read()
        recieve_char = recieve_char.decode("utf-8")
    return recieve_string


def move_arrays(serial_ports, parce_string, port):
    """Wait until the Arduino sends "Arduino Ready" - allows time for Arduino
    reset it also ensures that any bytes left over from a previous message are
    discarded"""
    try:
        move_arrays_execute(serial_ports, parce_string, port)
    except timeout_decorator.TimeoutError:
        SPINNER.write(
            "== == Array: "
            + str(port)
            + " \033[31m"
            + "EXECUTION FAILED TIMEOUT"
            + "\033[0m"
        )


@timeout_decorator.timeout(100, use_signals=False)
def move_arrays_execute(serial_ports, parce_string, port):
    """Sends commands Arduino and then waits for a reply. Created off move_arrays() so
    we can have both a timeout and a try catch block"""
    waiting_for_reply = False
    if not waiting_for_reply:
        serial_ports[port][1].write(parce_string.encode())
        SPINNER.write("-> -> Array: " + str(port) + " \033[32m" + "SENT" + "\033[0m")
        waiting_for_reply = True

    if waiting_for_reply:
        while serial_ports[port][1].inWaiting() == 0:
            pass
        data_recieved = recieve_from_arduino(serial_ports, port)
        SPINNER.write("<- <- Array: " + str(port) + " " + data_recieved)
        waiting_for_reply = False


def close_connections(serial_ports):
    """ Closes serial port(s)"""
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
                + " \033[32m"
                + "CLOSED"
                + "\033[0m"
            )
        except AttributeError:
            SPINNER.write(
                "Serial port "
                + str(count)
                + " "
                + serial_ports[count][0]
                + " \033[31m"
                + "FAILED"
                + "\033[0m"
            )
            SPINNER.stop()
    SPINNER.stop()


##############################################################################
##############################################################################
##############################################################################


def main():
    """ Main function of the program. Also provides tui in terminal to interact with
    """
    # address of USB port,pyserial object, array number, and number of motors
    serial_ports = []
    # need this for error checking in threads
    did_error_occur = False

    while True:
        # set to false on every loop
        did_error_occur = False
        # wait for user to want to run program
        input_text_1 = input(
            "\n\nPress Enter to Start the Program or type 'Exit' to Close:"
        )
        if input_text_1 in ("Exit", "exit"):
            break
        # find all usb devices connected at /dev/ttyU*
        # we are assuming that all usb devices at this address are arduinos
        did_error_occur, serial_ports = find_arduinos()
        # initialize serial_objecs size based on the number of arduinos
        if not did_error_occur:
            # open ports at address /dev/ttyU* that we found earlier
            did_error_occur, serial_ports = open_ports(serial_ports)
        if not did_error_occur:
            # check if the csvs for desired and current state exist
            print("\nChecking for CSV Files")
            did_error_occur = check_if_csvs_exist(DESIRED_STATE_FILENAME)
            did_error_occur = check_if_csvs_exist(CURRENT_STATE_FILENAME)
        if not did_error_occur:
            # lint csvs so that the contain valid data and are the coorect size
            did_error_occur = lint_csv_files(DESIRED_STATE_FILENAME)
            did_error_occur = lint_csv_files(CURRENT_STATE_FILENAME)
        if not did_error_occur:
            # connect to the arrays and then save the array number and number of motors
            did_error_occur, serial_ports = connect_to_arrays(serial_ports)
        if not did_error_occur:
            # lint the data we recieved from the arrays
            did_error_occur = lint_serial_port_values(serial_ports)
        # if error didn't occour exit this loop and move on to the next one
        if not did_error_occur:
            break
        # if we got to connecting to ports then close ports otherwise loop
        if len(serial_ports) != 0:
            close_connections(serial_ports)
    ###########
    while input_text_1 not in ("Exit", "exit"):
        print("===========\n")
        input_text_2 = input(
            "Enter '1' to set ceiling from csv, '2' to reset, and 'Exit' to close program)\n : "
        )
        # csv mode
        if input_text_2 == "1":
            print("CSV Mode\n")
            commands_from_csv(serial_ports)
        # csv reset
        elif input_text_2 == "2":
            print("CSV Reset Mode\n")
            commands_from_reset(serial_ports)
        # manual mode
        elif input_text_2 == "3":
            print("Manual Mode\n")
            execute_commands(
                serial_ports, input("Enter Commands (format '<Up,1>;<Up,1>'):\n : ")
            )
        # exit
        elif input_text_2 in ("Exit", "exit"):
            # close all serial connections
            close_connections(serial_ports)
            break
        else:
            print("Invalid Input\n")


# global variables
# never change
BAUD_RATE = 9600
START_MARKER = 60
END_MARKER = 62
SPINNER = yaspin(Spinners.weather)
# adjustable
MAX_TURNS = 10
MAX_NUMBER_OF_ARRAYS = 3
MAX_NUMBER_OF_MOTORS = 3
DESIRED_STATE_FILENAME = "desired_state.csv"
CURRENT_STATE_FILENAME = "current_state.csv"

if __name__ == "__main__":
    main()
