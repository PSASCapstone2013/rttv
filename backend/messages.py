import struct
import json

from config import *

delimiter = struct.Struct('!4sLH')              # 4 char, 2 short uint,
                                                # 4 long uint, 2 short uint

message_type = {
    'SEQN':     delimiter,                      # packet log separator
    'GPS\x01':  struct.Struct("<BBH 3d 5f HH"), # GPS BIN1
        # more details about GPS format here:
        # http://www.hemispheregps.com/gpsreference/Bin1.htm
    'ADIS':     struct.Struct(">12h"),          # ADIS16405 IMU
    'MPU9':     struct.Struct(">7H"),           # MPU9150 IMU
    'MPL3':     struct.Struct(">2L"),           # MPL3115A2 Pressure Sensor
    'ROLL':     struct.Struct("<HB")            # ROLL computer data
}


def json_GPS_bin1(message_id, timestamp, data):
    obj = {
        'fieldID': message_id,
        'timestamp': timestamp,
        'AgeOfDiff': data[0],
        'NumOfSats': data[1],
        'GPSWeek': data[2],
        'GPSTimeOfWeek': data[3],
        'Latitude': data[4],
        'Longitude': data[5],
        'Height': data[6],
        'VNorth': data[7],
        'VEast': data[8],
        'Vup': data[9],
        'StdDevResid': data[10],
        'NavMode': data[11],
        'ExtendedAgeOfDiff': data[12]
    }
    return obj

def json_ADIS(message_id, timestamp, data):
    obj = {
        'fieldID': message_id,
        'timestamp': timestamp,
        'PowerSupply': data[0],
        'GyroscopeX': data[1],
        'GyroscopeY': data[2],
        'GyroscopeZ': data[3],
        # 'gyroscope_magn': magnitude(data[1], data[2], data[3]),

        'AccelerometerX': data[4],
        'AccelerometerY': data[5],
        'AccelerometerZ': data[6],
        # 'accelerometer_magn': magnitude(data[4], data[5], data[6]),

        'MagnetometerX': data[7],
        'MagnetometerY': data[8],
        'MagnetometerZ': data[9],
        # 'MagnetometerMagn': magnitude(data[7], data[8], data[9]),

        'Temperature': data[10],
        'AuxiliaryADC': data[11]
    }
    return obj

def json_MPU9(message_id, timestamp, data):
    # This one has not been used
    obj = {
        'fieldID': message_id,
        'timestamp': timestamp,
        'field0': data[0],
        'field1': data[1],
        'field2': data[2],
        'field3': data[3],
        'field4': data[4],
        'field5': data[5],
        'field6': data[6],
    }
    return obj

def jsonMPL3(message_id, timestamp, data):
    # This one has not been used
    obj = {
        'fieldID': message_id,
        'timestamp': timestamp,
        'field0': data[0],
        'field1': data[1],
    }
    return obj

def json_ERRO(message_id, timestamp, data):
    # This message type has never been passed from the flight computer
    print "JSON ERRO message was generated."
    obj = {
        'fieldID': message_id,
        'timestamp': timestamp,
        'message': data,
    }
    return obj
    
def json_MESG(message_id, timestamp, data):
    obj = {
        'fieldID': message_id,
        'timestamp': timestamp,
        'message': data, # string
    }
    return obj
    
def jsonROLL(message_id, timestamp, data):
    obj = {
        'fieldID': message_id,
        'timestamp': timestamp,
        'finPosition': data[0], # servo PWM in microseconds
        'rollServoDisable': data[1], # boolean
    }
    return obj
    
def magnitude(x, y, z):
    return (x ** 2 + y ** 2 + z ** 2) ** 0.5
