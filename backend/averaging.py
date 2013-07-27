
import datetime
import sys

from messages import *
from config import *

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