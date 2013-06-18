
import datetime
import socket
import sys
import struct

IP_ADDRESS = ""
PORT = 36000
PACKET_SIZE = 4096

DEBUG = (sys.argv[1:] == ['-d']) 			# use '-d' option to display program output

tagHeader = struct.Struct('!4sHLH')			# 4 char, 2 short uint, 4 long uint, 2 short uint

messageType = {
	# TODO: need specification on how to treat those which return None
	'SEQN':     tagHeader,						# packet log separator
    'GPS\x01':  struct.Struct("<BBH 3d 5f HH"), # GPS BIN1
		# more details about GPS format here:
		# http://www.hemispheregps.com/gpsreference/Bin1.htm
    'ADIS':     struct.Struct(">12H"),			# ADIS16405 IMU
    'MPU9':     struct.Struct(">7H"),			# MPU9150 IMU
    'MPL3':     struct.Struct(">2L"),			# MPL3115A2 Pressure Sensor
	'ACC1':		None,							# Theo IMU, main accelerometer, 6 bytes (X, Y, Z)
	'ACC2':		None,							# Theo IMU, main accelerometer, 6 bytes (X, Y, Z)
	'GYRO':		None,							# Theo IMU, gyroscope (+ temp), 7 bytes (X, Y, Z, Temperature)
	'MAGN':		None,							# Theo IMU, magnetometer, 6 bytes (X, Y, Z)
	'ERRO':		None							# Error message, length of string error message.
}

def main():
	logFileName = datetime.datetime.now().strftime("log_%Y.%m.%d_%H-%M-%S")
	logFile = open(logFileName, "a")
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((IP_ADDRESS, PORT))
	lastSeq = sys.maxint
	counter = 0

	# listen socket
	while True:
		# receive packet
		message = sock.recv(PACKET_SIZE)

		# dump packet to log file
		logFile.write(tagHeader.pack('SEQN', 0, 0, len(message))) # add packet separator
		logFile.write(message)
		
		# get and check packet sequence number
		seq = int(message[0:4].encode('hex'), 16)             # sequence number (4 bytes)
		checkForLostPackets(seq, lastSeq)
		lastSeq = seq
		if DEBUG:
			print seq
		
		# packet may contain multiple messages
		message = message[4:]
		while len(message) > 0:
			# TODO: check endianness and signed/unsigned for these bytes:
			fieldID   = message[0:4]                          # four field ID charactes (4 bytes)
			timestamp = int(message[4:10].encode('hex'), 16)  # server timestamp (in ns) (6 bytes)
			length    = int(message[10:12].encode('hex'), 16) # data section length (in bytes) (2 bytes)
			data      = message[12:length+12]                 # data bytes

			if DEBUG:
				print "  %s %2d %.3f" % (fieldID, length, float(timestamp)/1e9), 
				
			processData(fieldID, timestamp, length, data)
				
			message = message [12+length:] # select the next message

		#exit() # TEMP: for debugging
		# TODO: define loop termination conditions (from front-end?)

def checkForLostPackets(seq, lastSeq):
	packetsLost = seq - lastSeq - 1
	if packetsLost > 0:
		print packetsLost, "packets were lost between", lastSeq, "and", seq
	# TODO: pass a message to front-end to notify about lost packets; need specifications

def processData(fieldID, length, timestamp, data):
	# parse data
	format = messageType.get(fieldID)
	if format == None or len(data) <> format.size: # validate data format
		if DEBUG:
			print "warning: unable to parse message of type", fieldID
		return # skip this message
	
	parsedData = format.unpack(data) # tuple containing parsed data
	if DEBUG:
		print repr(parsedData)
	
	# compute acceleration magnitude
	accelerationMagnitude = computeAccelerationMagnitude(fieldID, parsedData)
	if accelerationMagnitude <> None:
		# TODO: attach acceleration magnitude to the JSON object
		pass
	
	# TODO: pass parsed packet content to the front-end program
	
def computeAccelerationMagnitude(fieldID, parsedData):
	if fieldID == 'ADIS':
		x = parsedData[4]
		y = parsedData[5]
		z = parsedData[6]
	elif fieldID == 'ACC1':
		return None # TODO: need specifications here
	elif fieldID == 'ACC2':
		return None # TODO: need specifications here
	else:
		return None
		
	return (x ** 2 + y ** 2 + z ** 2) ** 0.5
	
if __name__ == "__main__":
    main()