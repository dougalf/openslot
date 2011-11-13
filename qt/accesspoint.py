# install to run:
#  sudo apt-get install python-qt4-doc
#  sudo apt-get install python-qt4-doc
#  sudo apt-get install qt4-qmlviewer
#  sudo apt-get install python-pyside
#  sudo apt-get install python-pyside.qtdeclarative
# and more ? python-serial

import os

from PySide import QtGui, QtDeclarative
from PySide.QtCore import QCoreApplication, QSocketNotifier, QTimer, SIGNAL
from PySide import QtCore, QtGui, QtDeclarative

import serial
import random
from struct import *

#serial port to use
DEVICE="/dev/ttyUSB0"
DEBUG=True
#incoming framesize
FRAMESIZE=15

#buffer incoming serial data
data=""
chk=0

def crc8(bytes):
	global chk
	
	ret=chr(chk)
	chk=(chk+1)&0xff
	#return(ret)
	TABLE=[
		0x00, 0x07, 0x0e, 0x09, 0x1c, 0x1b, 0x12, 0x15,
		0x38, 0x3f, 0x36, 0x31, 0x24, 0x23, 0x2a, 0x2d,
		0x70, 0x77, 0x7e, 0x79, 0x6c, 0x6b, 0x62, 0x65,
		0x48, 0x4f, 0x46, 0x41, 0x54, 0x53, 0x5a, 0x5d,
		0xe0, 0xe7, 0xee, 0xe9, 0xfc, 0xfb, 0xf2, 0xf5,
		0xd8, 0xdf, 0xd6, 0xd1, 0xc4, 0xc3, 0xca, 0xcd,
		0x90, 0x97, 0x9e, 0x99, 0x8c, 0x8b, 0x82, 0x85,
		0xa8, 0xaf, 0xa6, 0xa1, 0xb4, 0xb3, 0xba, 0xbd,
		0xc7, 0xc0, 0xc9, 0xce, 0xdb, 0xdc, 0xd5, 0xd2,
		0xff, 0xf8, 0xf1, 0xf6, 0xe3, 0xe4, 0xed, 0xea,
		0xb7, 0xb0, 0xb9, 0xbe, 0xab, 0xac, 0xa5, 0xa2,
		0x8f, 0x88, 0x81, 0x86, 0x93, 0x94, 0x9d, 0x9a,
		0x27, 0x20, 0x29, 0x2e, 0x3b, 0x3c, 0x35, 0x32,
		0x1f, 0x18, 0x11, 0x16, 0x03, 0x04, 0x0d, 0x0a,
		0x57, 0x50, 0x59, 0x5e, 0x4b, 0x4c, 0x45, 0x42,
		0x6f, 0x68, 0x61, 0x66, 0x73, 0x74, 0x7d, 0x7a,
		0x89, 0x8e, 0x87, 0x80, 0x95, 0x92, 0x9b, 0x9c,
		0xb1, 0xb6, 0xbf, 0xb8, 0xad, 0xaa, 0xa3, 0xa4,
		0xf9, 0xfe, 0xf7, 0xf0, 0xe5, 0xe2, 0xeb, 0xec,
		0xc1, 0xc6, 0xcf, 0xc8, 0xdd, 0xda, 0xd3, 0xd4,
		0x69, 0x6e, 0x67, 0x60, 0x75, 0x72, 0x7b, 0x7c,
		0x51, 0x56, 0x5f, 0x58, 0x4d, 0x4a, 0x43, 0x44,
		0x19, 0x1e, 0x17, 0x10, 0x05, 0x02, 0x0b, 0x0c,
		0x21, 0x26, 0x2f, 0x28, 0x3d, 0x3a, 0x33, 0x34,
		0x4e, 0x49, 0x40, 0x47, 0x52, 0x55, 0x5c, 0x5b,
		0x76, 0x71, 0x78, 0x7f, 0x6a, 0x6d, 0x64, 0x63,
		0x3e, 0x39, 0x30, 0x37, 0x22, 0x25, 0x2c, 0x2b,
		0x06, 0x01, 0x08, 0x0f, 0x1a, 0x1d, 0x14, 0x13,
		0xae, 0xa9, 0xa0, 0xa7, 0xb2, 0xb5, 0xbc, 0xbb,
		0x96, 0x91, 0x98, 0x9f, 0x8a, 0x8d, 0x84, 0x83,
		0xde, 0xd9, 0xd0, 0xd7, 0xc2, 0xc5, 0xcc, 0xcb,
		0xe6, 0xe1, 0xe8, 0xef, 0xfa, 0xfd, 0xf4, 0xf3
	]
	#start with first byte0
	crc8=TABLE[ord(bytes[0])]
	#for the rest of the bytes
	for char in bytes[1:]:
        #XOR table index
		crc8=TABLE[crc8^ord(char)]
	return chr(crc8)

# Handset class
class Handset:
    def __init__(self, index):
        self.index=index
        self.connected=False
        self.brake=False
        self.lanechange=False
        self.throttle=0

    def getConnected(self):
        return self.connected

    def setConnected(self, state):
        self.connected=state
        
    def getBrake(self):
        return self.brake

    def setBrake(self, state):
        self.brake=state

    def getLanechange(self):
        return self.lanechange
    
    def setLanechange(self, state):
        self.lanechange=state

    def getThrottle(self):
        return self.throttle
    
    def setThrottle(self, throttle):
        self.throttle=throttle

def updateGUI():
    for idx in range(0,6):
        root.updateDial(idx+1, handsets[idx].getThrottle()*2)

#six handsets
handsets=[Handset(1), Handset(2), Handset(3), Handset(4), Handset(5), Handset(6)]

def processFrame(frame):
        #verify checksum
        if crc8(frame[0:-1]) != frame[-1]:
            print "checksum error"
            #assume framing error reset input buffer
            data=""
            return
        # unpack , 9 bytes followed by integer (4bytes) and checksum(byte)
        (status,
        handset1,
        handset2,
        handset3,
        handset4,
        handset5,
        handset6,
        amps,
        sf,
        time,
	buttons,
        checksum)=unpack('<BBBBBBBBBIBB', frame)
        # connected state of each handset
        handsets[0].setConnected(bool(status&0x02))
        handsets[1].setConnected(bool(status&0x04))
        handsets[2].setConnected(bool(status&0x08))
        handsets[3].setConnected(bool(status&0x10))
        handsets[4].setConnected(bool(status&0x20))
        handsets[5].setConnected(bool(status&0x40))
        # track power status
        #track=bool(status&0x01)
        #brake status (bit 7)
        handsets[0].setBrake(bool((~handset1)&0x80))
        handsets[1].setBrake(bool((~handset2)&0x80))
        handsets[2].setBrake(bool((~handset3)&0x80))
        handsets[3].setBrake(bool((~handset4)&0x80))
        handsets[4].setBrake(bool((~handset5)&0x80))
        handsets[5].setBrake(bool((~handset6)&0x80))
        # lane change status (bit 6)
        handsets[0].setLanechange(bool((~handset1)&0x40))
        handsets[1].setLanechange(bool((~handset2)&0x40))
        handsets[2].setLanechange(bool((~handset3)&0x40))
        handsets[3].setLanechange(bool((~handset4)&0x40))
        handsets[4].setLanechange(bool((~handset5)&0x40))
        handsets[5].setLanechange(bool((~handset6)&0x40))
        # throttle (bit 5-0)
        handsets[0].setThrottle((~handset1)&0x3f)
        handsets[1].setThrottle((~handset2)&0x3f)
        handsets[2].setThrottle((~handset3)&0x3f)
        handsets[3].setThrottle((~handset4)&0x3f)
        handsets[4].setThrottle((~handset5)&0x3f)
        handsets[5].setThrottle((~handset6)&0x3f)
        # cardid of timer
        #self.cardid=self.sf&0x03
        #self.laptime=self.time*0.0000064  #6.4 us
	out=outframe()
	print ' '.join(['{:0>2x}'.format(ord(x)) for x in out])
	serport.write(out)

def processData(data):
    #process frames
    for idx in range (0, len(data)/FRAMESIZE):
        processFrame(data[idx*FRAMESIZE:(idx+1)*FRAMESIZE])
    

#try to increase timeout if <FRAMESIZE chunks are received    
def readAllData(fd):
        global data
        #empty the buffer into data
        while True:
            indata = serport.read(1024)
#            print "read :", len(indata)
            print ' '.join(['{:0>2x}'.format(ord(x)) for x in indata])
            if not indata:
                break
            #append to string buffer
            data=data+indata
        if len(data) >= FRAMESIZE:
            #handle chuncks of n*FRAMESIZE
#            print len(data)
            processData(data[0:(len(data)/FRAMESIZE)*FRAMESIZE])
            #keep remaining in buffer
            data=data[(len(data)/FRAMESIZE)*FRAMESIZE:]

toggle=False
def outframe():
    global toggle
    data=pack('BBBBBBBB', 
                        0xff,		#operation mode
                        ~((handsets[0].getThrottle()&0x3f)|({True:0x80, False:0}[handsets[0].getBrake()])|({True:0x40, False:0}[handsets[0].getLanechange()]))&0xff,
                        ~((handsets[1].getThrottle()&0x3f)|({True:0x80, False:0}[handsets[1].getBrake()])|({True:0x40, False:0}[handsets[1].getLanechange()]))&0xff,
                        ~((handsets[2].getThrottle()&0x3f)|({True:0x80, False:0}[handsets[2].getBrake()])|({True:0x40, False:0}[handsets[2].getLanechange()]))&0xff,
                        ~((handsets[3].getThrottle()&0x3f)|({True:0x80, False:0}[handsets[3].getBrake()])|({True:0x40, False:0}[handsets[3].getLanechange()]))&0xff,
                        ~((handsets[4].getThrottle()&0x3f)|({True:0x80, False:0}[handsets[4].getBrake()])|({True:0x40, False:0}[handsets[4].getLanechange()]))&0xff,
                        ~((handsets[5].getThrottle()&0x3f)|({True:0x80, False:0}[handsets[5].getBrake()])|({True:0x40, False:0}[handsets[5].getLanechange()]))&0xff,
                        ({True:0x80, False:0}[toggle])|
                        ({True:0x40, False:0}[not toggle])|
                        ({True:0x20, False:0}[handsets[5].getConnected()])|
                        ({True:0x10, False:0}[handsets[4].getConnected()])|
                        ({True:0x08, False:0}[handsets[3].getConnected()])|
                        ({True:0x04, False:0}[handsets[2].getConnected()])|
                        ({True:0x02, False:0}[handsets[1].getConnected()])|
                        ({True:0x01, False:0}[handsets[0].getConnected()]))
    #append checksum
    toggle=not toggle
    return data+crc8(data)

#six simulated handsets
simhandsets=[Handset(1), Handset(2), Handset(3), Handset(4), Handset(5), Handset(6)]

#for simulation only
def inframe():
    data=pack('<BbbbbbbBBIBB',
                            0xff,		#operation mode
                            ~((simhandsets[0].getThrottle()&0x3f)|({True:0x80, False:0}[simhandsets[0].getBrake()])|({True:0x40, False:0}[simhandsets[0].getLanechange()])),
                            ~((simhandsets[1].getThrottle()&0x3f)|({True:0x80, False:0}[simhandsets[1].getBrake()])|({True:0x40, False:0}[simhandsets[1].getLanechange()])),
                            ~((simhandsets[2].getThrottle()&0x3f)|({True:0x80, False:0}[simhandsets[2].getBrake()])|({True:0x40, False:0}[simhandsets[2].getLanechange()])),
                            ~((simhandsets[3].getThrottle()&0x3f)|({True:0x80, False:0}[simhandsets[3].getBrake()])|({True:0x40, False:0}[simhandsets[3].getLanechange()])),
                            ~((simhandsets[4].getThrottle()&0x3f)|({True:0x80, False:0}[simhandsets[4].getBrake()])|({True:0x40, False:0}[simhandsets[4].getLanechange()])),
                            ~((simhandsets[5].getThrottle()&0x3f)|({True:0x80, False:0}[simhandsets[5].getBrake()])|({True:0x40, False:0}[simhandsets[5].getLanechange()])),
                            #port current
                            128,
                            #SF
                            0xff,
                            #lap time 10s
                            int((1.0/0.0000064)*10),
                            0x00) #no buttons pressed ?
    return data+crc8(data)


count = 0

#for simulation
def timerexp():
#    out=outframe()
#    print ' '.join(['{:0>2x}'.format(ord(x)) for x in out])
#    serport.write(out)
    updateGUI()

if __name__ == '__main__':
    import sys

    #a = QCoreApplication([])
    QtGui.QApplication.setGraphicsSystem("raster")
    a = QtGui.QApplication(sys.argv)

#    #timeout minimum 1 jiffie ?
    serport=serial.Serial(port=DEVICE, baudrate=19200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=0.005)
    fd = serport.fileno()
    notifier = QSocketNotifier(fd, QSocketNotifier.Read)
    a.connect(notifier, SIGNAL('activated(int)'), readAllData)

    #time for test
    timer = QTimer()
    timer.start(100)
    timer.timeout.connect(timerexp)
    serport.write(outframe())   



    #setup QML
    view = QtDeclarative.QDeclarativeView()
    view.setSource(QtCore.QUrl('dialcontrol.qml'))
    root = view.rootObject()
    view.show()

    sys.exit(a.exec_())
