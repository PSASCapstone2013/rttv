import struct
import json

from config import *

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
    # This message type has never been used
    obj = {
        'fieldID': fieldID,
        'timestamp': timestamp,
        'message': data,
    }
    return obj
    
def jsonMESG(fieldID, timestamp, data):
    obj = {
        'fieldID': fieldID,
        'timestamp': timestamp,
        'message': data, # string
    }
    return obj
    
def jsonROLL(fieldID, timestamp, parsedData):
    obj = {
        'fieldID': fieldID,
        'timestamp': timestamp,
        'finPosition': parsedData[0], # servo PWM in microseconds
        'rollServoDisable': parsedData[1], # boolean
    }
    
def magnitude(x, y, z):
    return (x ** 2 + y ** 2 + z ** 2) ** 0.5