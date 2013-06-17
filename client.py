
import datetime
import socket
import sys

IP_ADDRESS = ""
PORT = 36000
PACKET_SIZE = 4096

def main():
	logFileName = datetime.datetime.now().strftime("logs\log %Y.%m.%d %H-%M-%S")
	logFile = open(logFileName, "a")
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((IP_ADDRESS, PORT))
	lastSeq = sys.maxint
	counter = 0

	# Listen socket
	while True:
		message   = sock.recv(PACKET_SIZE)                # packet contents
		seq       = int(message[0:4].encode('hex'), 16)   # packet sequence number (4 bytes)
		fieldId   = message[4:8]                          # four field ID charactes (4 bytes)
		length    = int(message[8:10].encode('hex'), 16)  # data section length (in bytes) (2 bytes)
		timestamp = int(message[10:16].encode('hex'), 16) # server timestamp (in ns) (6 bytes)
		data      = message[16:length+16]                 # data bytes
		
		print "%4d" %seq, fieldId, "%2d" % length, "%6.3f" %(float(timestamp) / 1e9)
		
		checkForLostPackets(seq, lastSeq)
		objectForFrontEnd = parseData(seq, fieldId, length, timestamp, data)
		# TODO: pass data to front-end
		# TODO: dump packets to logfile; specify format				
		# TODO: stayOn should be changed to False from the front-end program or after timeout.
		counter += 1
		if counter >= 100: # for debugging, terminate after receiving some number of packets
			break
		lastSeq = seq

def checkForLostPackets(seq, lastSeq):
	packetsLost = seq - lastSeq - 1
	if packetsLost > 0:
		print packetsLost, "packets were lost between", lastSeq, "and", seq
	# TODO: pass a  message to front-end to notify about lost packets

def parseData(seq, fieldId, length, timestamp, data):
	if fieldId == 'GPS\x01':
		return parseGPS(fieldId, length, data)
	if fieldId == 'ADIS':
		return parseADIS(fieldId, length, data)
	if fieldId == 'MPU9':
		return parseMPU9(fieldId, length, data)
	if fieldId == 'MPL3':
		return parseMPL3(fieldId, length, data)
	if fieldId == 'ACC1':
		return parseACC1(fieldId, length, data)
	if fieldId == 'ACC2':
		return parseACC2(fieldId, length, data)
	if fieldId == 'GYRO':
		return parseGYRO(fieldId, length, data)
	if fieldId == 'MAGN':
		return parseMAGN(fieldId, length, data)
	if fieldId == 'ERRO':
		return parseERRO(fieldId, length, data)
	else:
		print "field ID", fieldId, "is unknown"
		return None
		# TODO: generate warning for unknown field ID for the front-end program
	# TODO: pass parsed packet content to the front-end program
	
def parseGPS(fieldId, length, data):
	# TODO: need specifications to parse this one
	return None
	
def parseADIS(fieldId, length, data):
	return None

def parseMPU9(fieldId, length, data):
	# TODO: need specifications to parse this one
	return None
	
def parseMPL3(fieldId, length, data):
	# TODO: need specifications to parse this one
	return None
	
def parseACC1(fieldId, length, data):
	return None
	
def parseACC2(fieldId, length, data):
	return None
	
def parseGYRO(fieldId, length, data):
	return None
	
def parseMAGN(fieldId, length, data):
	return None
	
def parseERRO(fieldId, length, data):
	# TODO: need specifications to parse this one
	return None
	
if __name__ == "__main__":
    main()