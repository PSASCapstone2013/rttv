
from config import *
from averaging import *

def initSocket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP_ADDRESS, PORT))
    sock.settimeout(TIMEOUT)
    return sock

def receivePacket(sock):
    # receive packet
    try:
        message = sock.recv(PACKET_SIZE)
        return message
    except socket.timeout:
        if DEBUG and not BAD_DEBUG_ONLY:
            print "Timeout:", TIMEOUT, "seconds."
            print "Solution 1: check whether the server is running"
            print "Solution 2: check whether you are using the right port number"
        return ''

def checkSequenceNumber(message, lastSeq):
    # get and check packet sequence number
    seq = int(message[0:SEQUENCE_LENGTH].encode('hex'), 16)             # sequence number (4 bytes)
    
    temp = datetime.datetime.now()
    processData.packetAnalyze['PacketReceived'] = processData.packetAnalyze['PacketReceived'] + 1
    packetsLost = checkForLostPackets(seq, lastSeq, processData.packetAnalyze['latestPacketReceived'], temp)
    processData.packetAnalyze['PacketLost'].append(packetsLost)	
    processData.packetAnalyze['latestPacketReceived'] = temp
    
    lastSeq = seq
    if DEBUG and not BAD_DEBUG_ONLY:
        print seq, "(0x%.4x)" % seq
    return seq, lastSeq

def dumpPacketToLogFile(logFile, message, seq):
    # dump packet to log file
    logFile.write(delimiter.pack('SEQN', seq, len(message))) # add packet separator
    logFile.write(message)
    # TODO: need to figure out (define) delimiter format
        
def checkForLostPackets(seq, lastSeq, previousPacketReceived, latestPacketReceived):
    packetsLost = seq - lastSeq - 1
    obj = {}
    if packetsLost > 0:
        if DEBUG and not BAD_DEBUG_ONLY:
            print packetsLost, "packets were lost between", lastSeq, "and", seq
        # TODO: pass a message to front-end to notify about lost packets; need specifications
        obj = { 
            'From'      : previousPacketReceived.strftime('%H%M%S%f'),
            'To'  	: latestPacketReceived.strftime('%H%M%S%f'),
            'PacketLost': packetsLost
        }
    return obj

def parseMessageHeader(message):
    fieldID = message[FIELD_ID_OFFSET:TIMESTAMP_OFFSET]
    timestamp = int(message[TIMESTAMP_OFFSET:DATA_LENGTH_OFFSET].encode('hex'), 16)
    length = int(message[DATA_LENGTH_OFFSET:DATA_OFFSET].encode('hex'), 16) # data section length (in bytes) (2 bytes)            
    # print fieldID, FIELD_ID_OFFSET, TIMESTAMP_OFFSET
    # print timestamp, TIMESTAMP_OFFSET, DATA_LENGTH_OFFSET
    # print length, DATA_LENGTH_OFFSET, DATA_OFFSET
    # exit()
    return fieldID,timestamp, length
    
def overwriteLength(fieldID, length):
    # workaround for flight computer bug which puts wrong data length value into ADIS header
    if fieldID == 'ADIS':
        format = messageType.get(fieldID)
        newLength = format.size
        return newLength
    return length
    
def dataIsTruncated(message, lengthExpected):
    if len(message) < lengthExpected + HEADER_LENGTH: # message was truncated in its data
        # sys.stdout.write('t')
        return True
    return False
    
