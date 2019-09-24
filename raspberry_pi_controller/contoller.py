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

def sendToArduino(sendStr):
  ser.write(sendStr.encode())

#======================================

def runTest(td):
  waitingForReply = False

  if waitingForReply == False:
    sendToArduino(td)
    print ("-> -> -> -> -> ->")
    print ("Message Sent:")
    print ("PC: " + td)
    waitingForReply = True

  if waitingForReply == True:

    while ser.inWaiting() == 0:
      pass
      
    dataRecvd = recvFromArduino()
    print ("<- <- <- <- <- <-")
    print ("Message Received:  " + dataRecvd)
    waitingForReply = False

    time.sleep(.1)


#======================================
#======================================

import serial
import time
import sys


NUMBER_OF_SLAVES = 2
startMarker = 60
endMarker = 62
baudRate = 9600
serPort = ["/dev/cu.usbmodem1412101", "/dev/cu.usbmodem1412201"]
#serPort = "/dev/cu.SLAB_USBtoUART"
#serPort = "/dev/ttyUSB0"

ser = [None] * NUMBER_OF_SLAVES

for x in range(len(serPort)):
  ser[x] = serial.Serial(serPort[x], baudRate)
  # print(ser[x])
  print ("Serial port " + serPort[x] + " opened")

# Better Printout
print("")

for port in range(len(serPort)):
  waitForArduino(port)

#while 1 :
#    print ("===========")
#    print ("")
#    text = input("Up or Down?: ")
#    text = "<" + text + ">"
#    runTest(text)
#    time.sleep(1)

for x in range(len(serPort)):
  print ("Serial port " + serPort[x] + " closed")
  ser[x].close

