#=====================================

#  Function Definitions

#=====================================

def waitForArduino(port):

   # wait until the Arduino sends 'Arduino Ready' - allows time for Arduino reset
   # it also ensures that any bytes left over from a previous message are discarded
   
    global startMarker, endMarker
    
    msg = ""
    while msg.find("Arduino is ready") == -1:
      while ser[port].inWaiting() == 0:
        pass
      msg = recvFromArduino(port)
      print ("Arduino Number:", port, "Is Ready")
      print ("Message from Arduino:" + msg)
#======================================

def recvFromArduino(port):
  global startMarker, endMarker
  
  ck = ""
  x = "z" # any value that is not an end- or startMarker
  #byteCount = -1 # to allow for the fact that the last increment will be one too many
  x = ser[port].read()
  x = x.decode("utf-8")
  #print(x)
  # wait for the start character
  while  ord(x) != startMarker: 
    x = ser[port].read()
    x = x.decode("utf-8") 
    #print(x)
  # save data until the end marker is found
  while ord(x) != endMarker:
    if ord(x) != startMarker:
      ck = ck + x 
      #byteCount += 1
    x = ser[port].read()
    x = x.decode("utf-8") 
    #print(x) 
  return(ck)
  
#=====================================
# get rid of this function

def sendToArduino(sendStr, port):
  ser[port].write(sendStr.encode())

#======================================

def run(td,port):
  waitingForReply = False

  if waitingForReply == False:
    sendToArduino(td, port)
    print ("-> -> -> -> -> ->")
    print ("Message Sent:")
    print ("PC: " + td)
    waitingForReply = True

  if waitingForReply == True:

    while ser[port].inWaiting() == 0:
      pass
      
    dataRecvd = recvFromArduino(port)
    print ("<- <- <- <- <- <-")
    print ("Message Received:  " + dataRecvd)
    waitingForReply = False
    time.sleep(.1)


#======================================
#======================================

import serial
import time
import sys
from threading import Thread

# global variables
NUMBER_OF_SLAVES = 2
startMarker = 60
endMarker = 62
baudRate = 9600
# alternative serPort = "/dev/ttyUSB0"
serPort = ["/dev/cu.usbmodem1412101", "/dev/cu.usbmodem1412201"]

# initialize serial variable array
ser = [None] * NUMBER_OF_SLAVES
threads = [None] * NUMBER_OF_SLAVES

for x in range(len(serPort)):
  ser[x] = serial.Serial(serPort[x], baudRate)
  print ("Serial port " + serPort[x] + " opened")

print("")

for port in range(len(serPort)):
  waitForArduino(port)

while 1 :
    print ("===========")
    print ("")
    text = input("Enter Commands: ")
    parse_text = text.split(';')
    print (parse_text)
    
    # create threads
    for x in range(len(parse_text)):
      print (parse_text[x])
      print (x)
      threads[x] = Thread(target=run, args=(parse_text[x],x))

    # start threads
    for x in range(len(parse_text)):
      threads[x].start()

    # wait for threads to finish
    for x in range(len(parse_text)):
      threads[x].join()

    
# close all serial connections
for x in range(len(serPort)):
  print ("Serial port " + serPort[x] + " closed")
  ser[x].close
