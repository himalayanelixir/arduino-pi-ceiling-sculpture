#=====================================

#  Function Definitions

#=====================================

def sendToArduino(sendStr):
  ser.write(sendStr.encode())


#======================================

def recvFromArduino():
  global startMarker, endMarker
  
  ck = ""
  x = "z" # any value that is not an end- or startMarker
  #byteCount = -1 # to allow for the fact that the last increment will be one too many
  x = ser.read()
  x = x.decode("utf-8")
  #print(x)
  # wait for the start character
  while  ord(x) != startMarker: 
    x = ser.read()
    x = x.decode("utf-8") 
    #print(x)
  # save data until the end marker is found
  while ord(x) != endMarker:
    if ord(x) != startMarker:
      ck = ck + x 
      #byteCount += 1
    x = ser.read()
    x = x.decode("utf-8") 
    #print(x) 
  return(ck)
  

#============================

def waitForArduino():

   # wait until the Arduino sends 'Arduino Ready' - allows time for Arduino reset
   # it also ensures that any bytes left over from a previous message are discarded
   
    global startMarker, endMarker
    
    msg = ""
    while msg.find("Arduino is ready") == -1:

      while ser.inWaiting() == 0:
        pass
        
      msg = recvFromArduino()

      print (msg)
      print ("")
      
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

print ("")
print ("")

serPort = "/dev/cu.SLAB_USBtoUART"
#serPort = "/dev/ttyUSB0"
baudRate = 9600
ser = serial.Serial(serPort, baudRate)
print ("Serial port " + serPort + " opened  Baudrate " + str(baudRate))

startMarker = 60
endMarker = 62

waitForArduino()

while 1 :
    print ("===========")
    print ("")
    text = input("Up or Down?: ")
    text = "<" + text + ">"
    runTest(text)
    time.sleep(1)

ser.close

