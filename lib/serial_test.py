#quick serial port test
import serial
import time
import os

#from PySide import QtGui, QtDeclarative
from PySide.QtCore import QCoreApplication, QSocketNotifier, QTimer, SIGNAL


serport=serial.Serial(port='/dev/ttyUSB0', baudrate=115200, bytesize=8, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=0.0)

FRAMESIZE=4096
data="\x41"*FRAMESIZE


t0=time.time()
kb=0
sec=10.0

def timerexp():
	global kb
	print kb/sec, " bytes/sec"
	kb=0
	
def readData(fd):
	global kb
	ldata=serport.read(FRAMESIZE)
	kb=kb+len(ldata)

def writeData(fd):
	global data
	serport.write(data)

if __name__ == '__main__':
    import sys

    print "buffered", len(serport.read(100000))
    print "buffered", len(serport.read(100000))
    a = QCoreApplication([])
    fd=serport.fileno()
    read_notifier = QSocketNotifier(fd, QSocketNotifier.Read)
    write_notifier = QSocketNotifier(fd, QSocketNotifier.Write)
    a.connect(read_notifier, SIGNAL('activated(int)'), readData)
    a.connect(write_notifier, SIGNAL('activated(int)'), writeData)

    timer = QTimer()
    timer.start(sec*1000)
    timer.timeout.connect(timerexp)
    serport.write(data)


    sys.exit(a.exec_())
	
