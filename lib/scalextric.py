# This program is based on the specifications in the Sagentia document
#"C7042 Scalextric 6 Car Power Base SNC Communication Protocol"

# Status : very unlikely to work.

import serial
from struct import *

#serial port to use
DEVICE="/dev/ttyUSB0"
DEBUG=True

def crc8(bytes):
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
	#start with first byte
	crc8=ord(bytes[0])
	#for the rest of the bytes
	for char in bytes[1:]:
		crc8=crc8^TABLE[ord(byte)]
	return chr(crc8)

class Incoming:
	def __init__(self):
		self.status=0
		self.handset1=0
		self.handset2=0
		self.handset3=0
		self.handset4=0
		self.handset5=0
		self.handset6=0
		self.amps=0
		self.sf=0
		self.time=0
		self.checksum=0
	
	def read(self, port):
		# read 14 bytes from port
		data=port.read(14)
		if( len(data) != 14 ):
			if DEBUG:
				data="\x03\x00\x00\x00\x00\x1f\xf0\x13\xf8\x01\x02\x03\x04\x55"
			else:
				print "data length not right, change timeout or use blocking read ?"
				return
		# unpack , 9 bytes followed by integer (4bytes) and checksum(byte)
		(self.status,
		self.handset1,
		self.handset2,
		self.handset3,
		self.handset4,
		self.handset5,
		self.handset6,
		self.amps,
		self.sf,
		self.time,
		self.checksum)=unpack('<BBBBBBBBBIB', data)
		# connected state of each handset
		self.connected1=bool(self.status&0x02)
		self.connected2=bool(self.status&0x04)
		self.connected3=bool(self.status&0x08)
		self.connected4=bool(self.status&0x10)
		self.connected5=bool(self.status&0x20)
		self.connected6=bool(self.status&0x40)
		# track power status
		self.track=bool(self.status&0x01)
		#brake status (bit 7)
		self.brake1=bool((~self.handset1)&0x80)
		self.brake2=bool((~self.handset2)&0x80)
		self.brake3=bool((~self.handset3)&0x80)
		self.brake4=bool((~self.handset4)&0x80)
		self.brake5=bool((~self.handset5)&0x80)
		self.brake6=bool((~self.handset6)&0x80)
		# lane change status (bit 6)
		self.lanechange1=bool((~self.handset1)&0x40)
		self.lanechange2=bool((~self.handset2)&0x40)
		self.lanechange3=bool((~self.handset3)&0x40)
		self.lanechange4=bool((~self.handset4)&0x40)
		self.lanechange5=bool((~self.handset5)&0x40)
		self.lanechange6=bool((~self.handset6)&0x40)
		# throttle (bit 5-0)
		self.throttle1=(~self.handset1)&0x3f
		self.throttle2=(~self.handset2)&0x3f
		self.throttle3=(~self.handset3)&0x3f
		self.throttle4=(~self.handset4)&0x3f
		self.throttle5=(~self.handset5)&0x3f
		self.throttle6=(~self.handset6)&0x3f
		# cardid of timer
		self.cardid=self.sf&0x03
		self.laptime=self.time*0.0000064  #6.4 us

class Outgoing:
	def __init__(self):
		self.brake1=False
		self.brake2=False
		self.brake3=False
		self.brake4=False
		self.brake5=False
		self.brake6=False
		self.lanechange1=False
		self.lanechange2=False
		self.lanechange3=False
		self.lanechange4=False
		self.lanechange5=False
		self.lanechange6=False
		self.throttle1=0
		self.throttle2=0
		self.throttle3=0
		self.throttle4=0
		self.throttle5=0
		self.throttle6=0
		self.LED1=False
		self.LED2=False
		self.LED3=False
		self.LED4=False
		self.LED5=False
		self.LED6=False
		self.LED_RED=False
		self.LED_GREEN=False

	def write(self, port):
		#pack binary data, without checksum
		data=pack('BBBBBBBB', 
			0xff,		#operation mode
			(self.throttle1&0x3f)|({True:0x80, False:0}[self.brake1])|({True:0x40, False:0}[self.lanechange1]),
			(self.throttle2&0x3f)|({True:0x80, False:0}[self.brake2])|({True:0x40, False:0}[self.lanechange2]),
			(self.throttle3&0x3f)|({True:0x80, False:0}[self.brake3])|({True:0x40, False:0}[self.lanechange3]),
			(self.throttle4&0x3f)|({True:0x80, False:0}[self.brake4])|({True:0x40, False:0}[self.lanechange4]),
			(self.throttle5&0x3f)|({True:0x80, False:0}[self.brake5])|({True:0x40, False:0}[self.lanechange5]),
			(self.throttle6&0x3f)|({True:0x80, False:0}[self.brake6])|({True:0x40, False:0}[self.lanechange6]),
			({True:0x80, False:0}[self.LED_GREEN])|
			({True:0x40, False:0}[self.LED_RED])|
			({True:0x20, False:0}[self.LED1])|
			({True:0x10, False:0}[self.LED2])|
			({True:0x08, False:0}[self.LED3])|
			({True:0x04, False:0}[self.LED4])|
			({True:0x02, False:0}[self.LED5])|
			({True:0x01, False:0}[self.LED6]))
		#append checksum
		data=data+crc8(data)
		#write to port
		port.write(data)

if __name__ == "__main__":
	# 1 startbit, 1 stopbit, 19200 baud, 8 databits, no parity
	# maybe better to use hotpol and non-blocking reads ? 
	serport=serial.Serial(port=DEVICE, baudrate=19200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=0.010)

	#we have to send something to the BASE first
	outbase=Outgoing()
	#turn red led on
	outbase.LED_RED=True
	outbase.write(serport)

	inbase=Incoming()
	#now wait for result and keep it going
	while(True):
		inbase.read(serport)
		#only handle car1
		outbase.throttle1=inbase.throttle1
		outbase.brake1=inbase.brake1
		outbase.lanechange1=inbase.lanechange1
		outbase.write(serport)
