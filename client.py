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
PORT = 36000           # default port used in PSAS server-client example
#PORT = 35001           # port used by Ashley; didn't work with PSAS fake computer (Bogdan)
PACKET_SIZE = 4096     # maximum packet size to receive
TIMEOUT = 5            # time in seconds to wait for a packet
Count_mess = 1000      # the rate of transmitting message to the client's browser    

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

openWebSockets = []
openWebSocketsLock = thread.allocate_lock()

class FrontEndWebSocket(tornado.websocket.WebSocketHandler):
    def open(self):
        openWebSocketsLock.acquire()
        openWebSockets.append(self)
        self.list_position = len(openWebSockets) - 1
        openWebSocketsLock.release()
    def on_message(self,message):
        pass
    def on_close(self):
        openWebSocketsLock.acquire()
        openWebSockets.pop(self.list_position)
        openWebSocketsLock.release()

application = tornado.web.Application([
    (r"/", FrontEndWebSocket),
    ])

def tornadoThread(arg1, arg2):
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

    # listen socket
    while True:
        # receive packet
        print "receiving packets"
        try:
            message = sock.recv(PACKET_SIZE)
        except socket.timeout:
            print "Timeout:", TIMEOUT, "seconds."
            print "Solution 1: check whether the server is running"
            print "Solution 2: check whether you are using the right port number"
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
            if (jsonObj != None):
                sendJsonObj(jsonObj)

            message = message [12+length:] # select the next message 

            #exit() # TEMP: for debugging
            # TODO: define loop termination conditions (from front-end?)

def checkForLostPackets(seq, lastSeq):
    packetsLost = seq - lastSeq - 1
    if packetsLost > 0:
        print packetsLost, "packets were lost between", lastSeq, "and", seq
        # TODO: pass a message to front-end to notify about lost packets; need specifications

def initData():
    processData.GPS = 0
    processData.ADIS = 0
    processData.MPU9 = 0
    processData.MPL3 = 0
    processData.ADISmess = {}
    for i in ['X', 'Y', 'Z', 'Magn']:        
        processData.ADISmess['Gyroscope'+i] =  0
        processData.ADISmess['Accelerometer'+i] = 0
        processData.ADISmess['Magnetometer'+i] =0


def processData(fieldID, timestamp, length, data):

#for GPS, MPL3, MPU9 message: skip only send every 1000th message to the client's browser
#for ADIS message: average 1000 message, then send to the client's browser
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
        processData.GPS = processData.GPS + 1
        temp = jsonGPSbin1(fieldID, timestamp, parsedData)
        if ( processData.GPS == Count_mess):
            processData.GPS = 0
            return temp        
#get parsedData, then sum up 1000 messages before averaging them
    elif fieldID == 'ADIS':
        processData.ADIS = processData.ADIS + 1
        temp = jsonADIS(fieldID, timestamp, parsedData)
        if ( processData.ADIS == Count_mess):
            for i in ['X', 'Y', 'Z', 'Magn']:
                temp['Gyroscope'+i] = (temp['Gyroscope'+i] + processData.ADISmess['Gyroscope'+i] ) / Count_mess    
                temp['Accelerometer'+i] = (temp['Accelerometer'+i] + processData.ADISmess['Accelerometer'+i] ) / Count_mess    
                temp['Magnetometer'+i] = (temp['Magnetometer'+i] + processData.ADISmess['Magnetometer'+i] ) / Count_mess    
            processData.ADIS = 0
            processData.ADISmess['GyroscopeX'] = 0
            processData.ADISmess['GyroscopeY'] = 0
            processData.ADISmess['GyroscopeZ'] = 0
            return json.dumps(temp);
        else:
            for i in ['X', 'Y', 'Z', 'Magn']:
                processData.ADISmess['Gyroscope'+i] = (temp['Gyroscope'+i] + processData.ADISmess['Gyroscope'+i] )     
                processData.ADISmess['Accelerometer'+i] = (temp['Accelerometer'+i] + processData.ADISmess['Accelerometer'+i] )     
                processData.ADISmess['Magnetometer'+i] = (temp['Magnetometer'+i] + processData.ADISmess['Magnetometer'+i] ) 
    elif fieldID == 'MPU9':
        processData.MPU9 = processData.MPU9 + 1
        if ( processData.MPU9 == Count_mess):
            processData.MPU9 = 0;
            return jsonMPU9(fieldID, timestamp, parsedData)
        elif fieldID == 'MPL3':
            processData.MPL3 = processData.MPL3 + 1
        if ( processData.MPL3 == Count_mess):
            processData.MPL3 = 0
            return jsonMPL3(fieldID, timestamp, parsedData)
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
        # 'GyroscopeMagn': magnitude(parsedData[1], parsedData[2], parsedData[3]),
        'GyroscopeMagn' : 0,
        'AccelerometerX': parsedData[4],
        'AccelerometerY': parsedData[5],
        'AccelerometerZ': parsedData[6],
        # 'AccelerometerMagn': magnitude(parsedData[4], parsedData[5], parsedData[6]),
        'AccelerometerMagn': 0,
        'MagnetometerX': parsedData[7],
        'MagnetometerY': parsedData[8],
        'MagnetometerZ': parsedData[9],
        # 'MagnetometerMagn': magnitude(parsedData[7], parsedData[8], parsedData[9]),
        'MagnetometerMagn': 0,
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

# Send JSON object to the front-end application
def sendJsonObj(jsonObj):
    if jsonObj == None:
        return

    # To decode the JSON objects in Python, use:
    # objDecoded = json.loads(jsonObj)
    # print objDecoded['fieldID'], objDecoded['timestamp']
    openWebSocketsLock.acquire()
    for webSocket in openWebSockets:
        if webSocket is None:
            print "It is none"
        tornado.ioloop.IOLoop.instance().add_callback(webSocket.write_message, jsonObj)
    openWebSocketsLock.release()

if __name__ == "__main__":
    main()
