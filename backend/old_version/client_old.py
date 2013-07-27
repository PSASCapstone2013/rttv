import datetime
import socket
import sys
import struct
import json

import thread

import tornado.ioloop
import tornado.web
import tornado.websocket


IP_ADDRESS = ""        # dafault IP
PORT = 35001           # new port used in PSAS server-client example
#PORT = 36000           # old port used in PSAS server-client example
PACKET_SIZE = 4096     # maximum packet size to receive
TIMEOUT = 5            # time in seconds to wait for a packet
timeRate = 100000      # the rate of transmitting message to the client's browser    

DEBUG = (sys.argv[1:] == ['-d'])                # use '-d' option to display program output
BAD_DEBUG_ONLY = True                           # Show only debug information for bad cases
HEADER_LENGTH = 12                              # message header length

delimiter = struct.Struct('!4sLH')              # 4 char, 2 short uint, 4 long uint, 2 short uint

messageType = {
    'SEQN':     delimiter,                      # packet log separator
    'GPS\x01':  struct.Struct("<BBH 3d 5f HH"), # GPS BIN1
    # more details about GPS format here:
    # http://www.hemispheregps.com/gpsreference/Bin1.htm
    'ADIS':     struct.Struct(">12H"),          # ADIS16405 IMU
    'MPU9':     struct.Struct(">7H"),           # MPU9150 IMU
    'MPL3':     struct.Struct(">2L"),           # MPL3115A2 Pressure Sensor
    'ROLL':     struct.Struct("<HB")            # ROLL computer data
}


openWebSockets = [] #an array of open websocket connections
openWebSocketsLock = thread.allocate_lock() #lock used when accessing the thread running the Tornado code

class FrontEndWebSocket(tornado.websocket.WebSocketHandler):
    def open(self): #appends a new connection to the end of the array of connections and generates its position in the array 
        openWebSocketsLock.acquire()
        openWebSockets.append(self)
        self.list_position = len(openWebSockets) - 1
        openWebSocketsLock.release()
    def on_message(self,message):
        pass
    def on_close(self): #closes a connection in the array of connections by removing it from is position
        openWebSocketsLock.acquire()
        openWebSockets.pop(self.list_position)
        openWebSocketsLock.release()

application = tornado.web.Application([
    (r"/", FrontEndWebSocket),
])

def tornadoThread(arg1, arg2): #defines a thread that runs a Tornado IO loop that listens to port 8080
    application.listen(8080)
    tornado.ioloop.IOLoop.instance().start()

def main():
    if not DEBUG:
        print "In order to see output, run it as 'python client.py -d'"

    logFileName = datetime.datetime.now().strftime("log_%Y.%m.%d_%H-%M-%S")
    logFile = open(logFileName, "a")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP_ADDRESS, PORT))
    sock.settimeout(TIMEOUT)
    lastSeq = sys.maxint
    thread.start_new_thread(tornadoThread, (0,0))
    initData()
    startTime = datetime.datetime.now()

    # listen socket
    while True:
        # receive packet
        try:
            message = sock.recv(PACKET_SIZE)
        except socket.timeout:
            if DEBUG and not BAD_DEBUG_ONLY:
                print "Timeout:", TIMEOUT, "seconds."
                print "Solution 1: check whether the server is running"
                print "Solution 2: check whether you are using the right port number"
            # TODO: Let front-end know about timeout if needed
            continue # stay in the loop and wait for another packet

        if DEBUG and BAD_DEBUG_ONLY:
            printDot()

        # get and check packet sequence number
        seq = int(message[0:4].encode('hex'), 16)             # sequence number (4 bytes)
        temp = datetime.datetime.now()
        processData.packetAnalyze['PacketReceived'] = processData.packetAnalyze['PacketReceived'] + 1
        packetsLost = checkForLostPackets(seq, lastSeq,processData.packetAnalyze['latestPacketReceived'], temp)
        processData.packetAnalyze['PacketLost'].append(packetsLost)	
        processData.packetAnalyze['latestPacketReceived'] = temp
        lastSeq = seq
        if DEBUG and not BAD_DEBUG_ONLY:
            print seq, "(0x%.4x)" % seq

        # dump packet to log file
        logFile.write(delimiter.pack('SEQN', seq, len(message))) # add packet separator
        logFile.write(message)
        # TODO: need to figure out delimiter format

        # packet may contain multiple messages
        message = message[4:]
        while len(message) > HEADER_LENGTH: # safe from messages truncated in the middle of their header
            fieldID = message[0:4]                            # four field ID charactes (4 bytes)
            timestamp = int(message[4:10].encode('hex'), 16)  # server timestamp (in ns) (6 bytes)
            length = int(message[10:12].encode('hex'), 16)    # data section length (in bytes) (2 bytes)            

            # workaround for flight computer bug which puts wrong data length value into ADIS header
            if fieldID == 'ADIS':
                format = messageType.get(fieldID)
                length = format.size
            if len(message) < length + HEADER_LENGTH: # safe from messages truncated in the middle of their data
                break # go to next packet

            data = message[HEADER_LENGTH:length+HEADER_LENGTH] # data bytes

            if DEBUG and not BAD_DEBUG_ONLY:
                print "  %s %2d %.3f" % (fieldID, length, float(timestamp)/1e9), 

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

            startTime = datetime.datetime.now()

            message = message [HEADER_LENGTH+length:] # select the next message 

            # TODO: define loop termination conditions (from front-end?)


def noPacketReceived():
    if (( processData.ADISMess == {}) and ( processData.lastGPSMess == {}) and (processData.lastMPL3Mess == {}) and (processData.lastMPU9 == {})):
        return True
    return False


def checkBeforeSend(jsonObj, fieldID):
    if (fieldID == 'ADIS'):

        for i in ['X', 'Y', 'Z']:
            jsonObj['Gyroscope'+i] = (jsonObj['Gyroscope'+i]  ) / processData.ADISCount    
            jsonObj['Accelerometer'+i] = (jsonObj['Accelerometer'+i]  ) / processData.ADISCount    
            jsonObj['Magnetometer'+i] = (jsonObj['Magnetometer'+i]  ) / processData.ADISCount	

        jsonObj['GyroscopeMagn'] = magnitude(jsonObj['GyroscopeX'], jsonObj['GyroscopeY'], jsonObj['GyroscopeZ'])
        jsonObj['AccelerometerMagn'] = magnitude(jsonObj['AccelerometerX'], jsonObj['AccelerometerY'], jsonObj['AccelerometerZ'])
        jsonObj['MagnetometerMagn'] = magnitude(jsonObj['MagnetometerX'], jsonObj['MagnetometerY'], jsonObj['MagnetometerZ'])
        initData()
    return jsonObj


def checkForLostPackets(seq, lastSeq, previousPacketReceived, latestPacketReceived):
    packetsLost = seq - lastSeq - 1
    obj = {}
    if packetsLost > 0:
        if DEBUG and not BAD_DEBUG_ONLY:
            print packetsLost, "packets were lost between", lastSeq, "and", seq
        # TODO: pass a message to front-end to notify about lost packets; need specifications
        obj = { 
            'From'      : previousPacketReceived,
            'To'  	: latestPacketReceived,
            'PacketLost': packetLost
        }
    return obj



def initData():
    processData.packetAnalyze = initPacketAnalyze()
    processData.lastGPSMess = {}
    processData.lastMPU9Mess = {}
    processData.lastMPL3Mess = {}
    processData.ADISCount = 0
    processData.ADISMess = {}
    for i in ['X', 'Y', 'Z', 'Magn']:        
        processData.ADISMess['Gyroscope'+i] =  0
        processData.ADISMess['Accelerometer'+i] = 0
        processData.ADISMess['Magnetometer'+i] =0

def processData(fieldID, timestamp, length, data):


    # handle error message
    if fieldID == 'ERRO':
        return jsonERRO(fieldID, timestamp, data)

    # parse data
    format = messageType.get(fieldID)
    if format == None or len(data) <> format.size: # validate data format
        if(fieldID == 'ADIS'): # This ADIS is truncted by the fragmented packet. Not my fault!
            return None # quitely skip it
        if DEBUG:
            print "  warning: unable to parse message of type", fieldID
            # print "    unknown format:", format == None
            # print "    data length:", len(data)
            # print "    format size:", format.size
        return None # skip this message

    parsedData = format.unpack(data) # tuple containing parsed data
    if DEBUG and not BAD_DEBUG_ONLY:
        print repr(parsedData)


    if fieldID == 'SEQN':
        return None # skip

    elif fieldID == 'GPS\x01':
        processData.lastGPSMess = jsonGPSbin1(fieldID, timestamp, parsedData)

#get parsedData, then sum up 1000 messages before averaging them
    elif fieldID == 'ADIS':
        temp = jsonADIS(fieldID, timestamp, parsedData)
        for i in ['X', 'Y', 'Z']:
            processData.ADISMess['Gyroscope'+i] = (temp['Gyroscope'+i] + processData.ADISMess['Gyroscope'+i] )     
            processData.ADISMess['Accelerometer'+i] = (temp['Accelerometer'+i] + processData.ADISMess['Accelerometer'+i] )     
            processData.ADISMess['Magnetometer'+i] = (temp['Magnetometer'+i] + processData.ADISMess['Magnetometer'+i] ) 
        processData.ADISCount = processData.ADISCount + 1
        processData.ADISMess = temp

    elif fieldID == 'MPU9':
        processData.lastMPU9Mess = jsonMPU9(fieldID, timestamp, parsedData)

    elif fieldID == 'MPL3':
        processData.lastMPL3Mess = jsonMPL3(fieldID, timestamp, parsedData)


def initPacketAnalyze():
    obj = {
        'fieldID': 'Analyze',
        'PacketReceived': 0,
        'latestPacketReceived': datetime.datetime.now(),
        'PacketLost':[],
    }
    return obj


def jsonGPSbin1(fieldID, timestamp, parsedData):
    obj = {
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
    }
    return obj

def jsonADIS(fieldID, timestamp, parsedData):
    obj = {
        'fieldID': fieldID,
        'timestamp': timestamp,
        'PowerSupply': parsedData[0],
        'GyroscopeX': parsedData[1],
        'GyroscopeY': parsedData[2],
        'GyroscopeZ': parsedData[3],
        # 'GyroscopeMagn': magnitude(parsedData[1], parsedData[2], parsedData[3]),

        'AccelerometerX': parsedData[4],
        'AccelerometerY': parsedData[5],
        'AccelerometerZ': parsedData[6],
        # 'AccelerometerMagn': magnitude(parsedData[4], parsedData[5], parsedData[6]),

        'MagnetometerX': parsedData[7],
        'MagnetometerY': parsedData[8],
        'MagnetometerZ': parsedData[9],
        # 'MagnetometerMagn': magnitude(parsedData[7], parsedData[8], parsedData[9]),

        'Temperature': parsedData[10],
        'AuxiliaryADC': parsedData[11]
    }
    return obj

def jsonMPU9(fieldID, timestamp, parsedData):
    # TODO: ask sponsots about field names
    obj = {
        'fieldID': fieldID,
        'timestamp': timestamp,
        'field0': parsedData[0],
        'field1': parsedData[1],
        'field2': parsedData[2],
        'field3': parsedData[3],
        'field4': parsedData[4],
        'field5': parsedData[5],
        'field6': parsedData[6],
    }
    return obj

def jsonMPL3(fieldID, timestamp, parsedData):
    # TODO: ask sponsots about field names
    obj = {
        'fieldID': fieldID,
        'timestamp': timestamp,
        'field0': parsedData[0],
        'field1': parsedData[1],
    }
    return obj

def jsonERRO(fieldID, timestamp, data):
    # TODO: data format needs to be specified
    obj = {
        'fieldID': fieldID,
        'timestamp': timestamp,
        'message': data,
    }
    return obj

def magnitude(x, y, z):
    return (x ** 2 + y ** 2 + z ** 2) ** 0.5

# Send JSON object to the front-end application
def sendJsonObj(jsonObj):
    if jsonObj == None:
        return

    # To decode the JSON objects in Python, use:
    # objDecoded = json.loads(jsonObj)
    # print objDecoded['fieldID'], objDecoded['timestamp']
    openWebSocketsLock.acquire() 
    for webSocket in openWebSockets: #iterates through every open connections in the array
        if webSocket is None: #if the connection is null
            print "It is none"
        tornado.ioloop.IOLoop.instance().add_callback(webSocket.write_message, json.dumps(jsonObj)) #creates a write event that will run during the next iteration
                                                                                                    #of the Tornado io loop. The event will send the json object
                                                                                                    #to the front end. See http://www.tornadoweb.org/en/stable/ioloop.html#callbacks-and-timeouts
                                                                                                    #and http://www.tornadoweb.org/en/stable/websocket.html?highlight=websockets#output
                                                                                                    #and http://docs.python.org/2/library/json.html#basic-usage
                                                                                                    #for more detailed info

def printDot():
    # ================================= debug output =================================
    printDot.time_str = datetime.datetime.now().strftime("%H:%M:%S")
    if printDot.time_str_prev <> printDot.time_str:
        if printDot.total > 0:
            print "(%d)" % printDot.total
        printDot.total = 0
        print printDot.time_str, "",
    sys.stdout.write('.')
    printDot.total += 1
    printDot.time_str_prev = printDot.time_str
    # ================================================================================
printDot.total = 0
printDot.time_str = ""
printDot.time_str_prev = ""


if __name__ == "__main__":
    main()