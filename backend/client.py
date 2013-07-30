# modularization part
from config import *
from parsing import *
from averaging import *
from back_to_front import *

# to be modularized

def main():
    thread.start_new_thread(tornadoThread, (0,0))
    receivePackets()
    
def receivePackets():
    logFile = open(LOG_FILE_FORMAT, "a")
    sock = initSocket()
    initData()
    lastSeq = sys.maxint

    # listen socket
    while True:
        message = receivePacket(sock)
        if message == '': # timeout - no packets received during TIMEOUT
            # sendDataToFrontEnd('') # not sure how to make this one to work here
            continue # get the next packet
        debug.printChar('.') # packet received successfully --> print a dot
        seq, lastSeq = checkSequenceNumber(message, lastSeq)
        dumpPacketToLogFile(logFile, message, seq)
        
        # parse messages from the packet
        message = message[SEQUENCE_LENGTH:]
        while len(message) > HEADER_LENGTH: # end of data or message was truncated in its header
            fieldID, timestamp, length = parseMessageHeader(message)
            length = overwriteLength(fieldID, length)
            if dataIsTruncated(message, length):
                break # skip this message and read the next packet
            data = message[HEADER_LENGTH:length+HEADER_LENGTH] # data bytes
            debug.messageHeader(fieldID, length, timestamp) # print debug message
            jsonObj = processData(fieldID, timestamp, length, data)
            sendDataToFrontEnd(fieldID)
            message = message [HEADER_LENGTH+length:] # select the next message 

def sendDataToFrontEnd(fieldID):
    endTime = datetime.datetime.now()
    if ((endTime - sendDataToFrontEnd.startTime).microseconds > TIME_RATE):
        if(noPacketReceived()):
            sendJsonObj(jsonERRO('ERRO',0,"no packet revceived"))
            print "No packet received"
        else:
            sendJsonObj(checkBeforeSend(processData.ADISMess, fieldID))
            sendJsonObj(processData.lastGPSMess)
            sendJsonObj(processData.lastMPL3Mess)
            sendJsonObj(processData.lastMPU9Mess)
        sendJsonObj(checkBeforeSend(processData.packetAnalyze, 'Analyze'))
        initData()
    sendDataToFrontEnd.startTime = datetime.datetime.now()            
sendDataToFrontEnd.startTime = datetime.datetime.now() #executed at program initialization

if __name__ == "__main__":
    main()
