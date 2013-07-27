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
    startTime = datetime.datetime.now()

    # listen socket
    while True:
        message = receivePacket(sock)
        if message == '':
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

            # ==============================================
            # TODO: We need to move this part of code to a separate function when the bugs are fixed
            # This code is commented out because sendJsonObj() makes client.py to hang up
            ''' 
            jsonObj = processData(fieldID, timestamp, length, data)
            endTime = datetime.datetime.now()
            if ( (endTime - startTime).microseconds > timeRate):
                if(noPacketReceived()):
                    sendJsonObj(jsonERRO('ERRO',0,"no packet revceived"))
                    print "No packet received"
                else:
                    sendJsonObj(checkBeforeSend(processData.ADISMess, fieldID))
                    sendJsonObj(processData.lastGPSMess)
                    sendJsonObj(processData.lastMPL3Mess)
                    sendJsonObj(processData.lastMPU9Mess)
                sendJsonObj(processData.packetAnalyze)
                initData()
            '''
            # ==============================================
            
            startTime = datetime.datetime.now()            
            message = message [HEADER_LENGTH+length:] # select the next message 
            
if __name__ == "__main__":
    main()