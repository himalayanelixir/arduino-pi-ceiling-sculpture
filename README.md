# Arduino Raspberry Pi Ceiling Sculpture

The function of this code is to run a ceiling sculpture using a Raspberry Pi as a master and multiple Arduinos as slaves. Due to the nature of the code you could adapt this for any project that uses a text ui and cvs to send commands to an Arduino.  

![Diagram](https://raw.githubusercontent.com/himalayanelixir/arduino-pi-ceiling-sculpture/master/resources/arduino-pi-ceiling-sculpture-diagram.png)

# Setup

## Arduino

In the repo you will find the Arduino code under ```/arduino/arduino.ino```. Open this in the Arduino IDE and flash to the devices you are using. 

If using the Arduino cli it should look like this: 

![Diagram](https://raw.githubusercontent.com/himalayanelixir/arduino-pi-ceiling-sculpture/master/resources/arduino-upload.gif)

There are only a few variables that need to be modified to get this working. Note that in this project and array refers to the combination of an Arduino and the motors that are connected to it. Each motor consists of a servo motor, and encoder switch, and a reset switch. 

| Variable                       | Default          | Description                                                                                                                                                                          |
|--------------------------------|------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| DEBOUNCE_TIME                  | 0.4              | modifies the debounce time of the switches in the encoder. It is an arbretary number and changed depening on the switches used for the encoder and reset.                            |
| ARRAY_NUMBER                   | 0                | every array in the instala`tion must have a unique array number that is between 0 and MAX_ARRAY_NUMBER (set on the Raspberry Pi)                                                     |
| NUMBER_OF_MOTORS               | 1                | number of motors that you want to connect to this array                                                                                                                              |
| NUMBER_OF_MOTORS_MOVING        | 1                | the execution of the commands is staggarded/ cscading way from motor number 0 to NUMBER_OF_MOTORS. This is done to limit the amount of power being drawn at any one time on an array |
| TIMEOUT                        | 50000            | this number counts the number of loops before the array returns a timeout error to the raspberry pi. This is an arbirary number and should be adjusted depending on what you need.   |
| IGNORE_INPUT_TIME              | 150              | once the reset is hit we ignore inputs from the encoder switch for a certain number of loops. This is done so we skip an edge when moving down one turn from a reset event.          |
| int ports[NUMBER_OF_MOTORS][3] | { { 8, 9, 10 } } | mapping of the motors to Arduino pins. Add values corresponding to the number of motors you have connected. They are in the order motor, counter, reset.                         |

## Raspberry Pi

The Raspberry Pi setup is mostly automated using the script found at ```raspberry-pi/image-setup/firstboot.sh```. In the current setup I have an Raspberry connected to an Adafruit PiTFT Plus screen (https://www.adafruit.com/product/2298). If you aren't using the screen you can comment out those parts of the ```firstboot.sh``` script.  Also you can comment out the parts where it sets up the ```/raspberry-pi/gui.py``` file for the screen.

The best way to get everything working properly is to follow these steps:
1. Download the latest image from https://github.com/nmcclain/raspberian-firstboot/releases
2. Use etcher to write to SD card
3. Copy over `firstboot.sh` and `wpa_supplicant.conf` to boot partition of SD card. Remember to edit the `wpa_supplicant.conf` file with the details for your wifi network
4. Put SD card into Raspberry Pi and boot. This will take a while but but shouldn't take more than 30mins. If it does something probably went wrong. 
