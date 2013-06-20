import datetime
import socket
import sys
import struct
import json

IP_ADDRESS = ""        # dafault IP
PORT = 36000           # port which socket listens for packets
PACKET_SIZE = 4096     # maximum packet size to receive
TIMEOUT = 5            # time in seconds to wait for a packet

DEBUG = (sys.argv[1:] == ['-d'])                # use '-d' option to display program output

delimiter = struct.Struct('!4sLH')              # 4 char, 2 short uint, 4 long uint, 2 short uint

messageType = {
	'SEQN':     delimiter,                      # packet log separator
	'GPS\x01':  struct.Struct("<BBH 3d 5f HH"), # GPS BIN1
		# more details about GPS format here:
		# http://www.hemispheregps.com/gpsreference/Bin1.htm
	'ADIS':     struct.Struct(">12H"),          # ADIS16405 IMU
	'MPU9':     struct.Struct(">7H"),           # MPU9150 IMU
	'MPL3':     struct.Struct(">2L"),           # MPL3115A2 Pressure Sensor
}

def main():
	if not DEBUG:
		print "In order to see output, use:"
		print "python client.py -d"

	logFileName = datetime.datetime.now().strftime("log_%Y.%m.%d_%H-%M-%S")
	logFile = open(logFileName, "a")
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((IP_ADDRESS, PORT))
	sock.settimeout(TIMEOUT)
	lastSeq = sys.maxint
	counter = 0

	# listen socket
	while True:
		# receive packet
		try:
			message = sock.recv(PACKET_SIZE)
		except socket.timeout:
			print "Timeout:", TIMEOUT, "seconds."
			# TODO: Let front-end know about timeout if needed
			continue # stay in the loop and wait for another packet

		# get and check packet sequence number
		seq = int(message[0:4].encode('hex'), 16)             # sequence number (4 bytes)
		checkForLostPackets(seq, lastSeq)
		lastSeq = seq
		if DEBUG:
			print seq
		
		# dump packet to log file
		logFile.write(delimiter.pack('SEQN', seq, len(message))) # add packet separator
		logFile.write(message)
		# TODO: need to figure out delimiter format
		
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
			
			jsonObj = processData(fieldID, timestamp, length, data)
			sendJsonObj(jsonObj)
				
			message = message [12+length:] # select the next message 

		#exit() # TEMP: for debugging
		# TODO: define loop termination conditions (from front-end?)

def checkForLostPackets(seq, lastSeq):
	packetsLost = seq - lastSeq - 1
	if packetsLost > 0:
		print packetsLost, "packets were lost between", lastSeq, "and", seq
	# TODO: pass a message to front-end to notify about lost packets; need specifications

def processData(fieldID, timestamp, length, data):
	# handle error message
	if fieldID == 'ERRO':
		return jsonERRO(fieldID, timestamp, data)

	# parse data
	format = messageType.get(fieldID)
	if format == None or len(data) <> format.size: # validate data format
		if DEBUG:
			print "warning: unable to parse message of type", fieldID
		return None # skip this message
	
	parsedData = format.unpack(data) # tuple containing parsed data
	if DEBUG:
		print repr(parsedData)
	
	if fieldID == 'SEQN':
		return None # skip
	elif fieldID == 'GPS\x01':
		return jsonGPSbin1(fieldID, timestamp, parsedData)
	elif fieldID == 'ADIS':
		return jsonADIS(fieldID, timestamp, parsedData)
	elif fieldID == 'MPU9':
		return jsonMPU9(fieldID, timestamp, parsedData)
	elif fieldID == 'MPL3':
		return jsonMPL3(fieldID, timestamp, parsedData)
	else:
		return None
		
def jsonGPSbin1(fieldID, timestamp, parsedData):
	obj = json.dumps({
		'fieldID': fieldID,
		'timestamp': timestamp,
		'AgeOfDiff': parsedData[0],
		'NumOfSats': parsedData[1],
		'GPSWeek': parsedData[2],
		'GPSTimeOfWeek': parsedData[3],
		'Latitude': parsedData[4],
		'Longitude': parsedData[5],
		'Height': parsedData[6],
		'VNorth': parsedData[7],
		'VEast': parsedData[8],
		'Vup': parsedData[9],
		'StdDevResid': parsedData[10],
		'NavMode': parsedData[11],
		'ExtendedAgeOfDiff': parsedData[12]
	})
	return obj
	
def jsonADIS(fieldID, timestamp, parsedData):
	obj = json.dumps({
		'fieldID': fieldID,
		'timestamp': timestamp,
		'PowerSupply': parsedData[0],
		'GyroscopeX': parsedData[1],
		'GyroscopeY': parsedData[2],
		'GyroscopeZ': parsedData[3],
		'GyroscopeMagn': magnitude(parsedData[1], parsedData[2], parsedData[3]),
		'AccelerometerX': parsedData[4],
		'AccelerometerY': parsedData[5],
		'AccelerometerZ': parsedData[6],
		'AccelerometerMagn': magnitude(parsedData[4], parsedData[5], parsedData[6]),
		'MagnetometerX': parsedData[7],
		'MagnetometerY': parsedData[8],
		'MagnetometerZ': parsedData[9],
		'MagnetometerMagn': magnitude(parsedData[7], parsedData[8], parsedData[9]),
		'Temperature': parsedData[10],
		'AuxiliaryADC': parsedData[11]
	})
	return obj

def jsonMPU9(fieldID, timestamp, parsedData):
	# TODO: ask sponsots about field names
	obj = json.dumps({
		'fieldID': fieldID,
		'timestamp': timestamp,
		'field0': parsedData[0],
		'field1': parsedData[1],
		'field2': parsedData[2],
		'field3': parsedData[3],
		'field4': parsedData[4],
		'field5': parsedData[5],
		'field6': parsedData[6],
	})
	return obj

def jsonMPL3(fieldID, timestamp, parsedData):
	# TODO: ask sponsots about field names
	obj = json.dumps({
		'fieldID': fieldID,
		'timestamp': timestamp,
		'field0': parsedData[0],
		'field1': parsedData[1],
	})
	return obj
	
def jsonERRO(fieldID, timestamp, data):
	# TODO: data format needs to be specified
	obj = json.dumps({
		'fieldID': fieldID,
		'timestamp': timestamp,
		'message': data,
	})
	return obj
	
def magnitude(x, y, z):
	return (x ** 2 + y ** 2 + z ** 2) ** 0.5
	
def sendJsonObj(jsonObj):
	if jsonObj == None:
		return
	
	
	# TODO: send JSON object to the front-end application from this function

	# To decode the JSON objects in Python, use:
	# objDecoded = json.loads(jsonObj)
	# print objDecoded['fieldID'], objDecoded['timestamp']
		
	
if __name__ == "__main__":
    main()
