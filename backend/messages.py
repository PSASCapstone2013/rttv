import struct
import json

from config import *

delimiter = struct.Struct('!4sLH')              # 4 char, 2 short uint, 4 long uint, 2 short uint

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


def json_GPS_bin1(message_id, timestamp, parsed_data):
    obj = {
        'fieldID': message_id,
        'timestamp': timestamp,
        'AgeOfDiff': parsed_data[0],
        'NumOfSats': parsed_data[1],
        'GPSWeek': parsed_data[2],
        'GPSTimeOfWeek': parsed_data[3],
        'Latitude': parsed_data[4],
        'Longitude': parsed_data[5],
        'Height': parsed_data[6],
        'VNorth': parsed_data[7],
        'VEast': parsed_data[8],
        'Vup': parsed_data[9],
        'StdDevResid': parsed_data[10],
        'NavMode': parsed_data[11],
        'ExtendedAgeOfDiff': parsed_data[12]
    }
    return obj

def json_ADIS(message_id, timestamp, parsed_data):
    obj = {
        'fieldID': message_id,
        'timestamp': timestamp,
        'PowerSupply': parsed_data[0],
        'GyroscopeX': parsed_data[1],
        'GyroscopeY': parsed_data[2],
        'GyroscopeZ': parsed_data[3],
        # 'gyroscope_magn': magnitude(parsed_data[1], parsed_data[2], parsed_data[3]),

        'AccelerometerX': parsed_data[4],
        'AccelerometerY': parsed_data[5],
        'AccelerometerZ': parsed_data[6],
        # 'accelerometer_magn': magnitude(parsed_data[4], parsed_data[5], parsed_data[6]),

        'MagnetometerX': parsed_data[7],
        'MagnetometerY': parsed_data[8],
        'MagnetometerZ': parsed_data[9],
        # 'MagnetometerMagn': magnitude(parsed_data[7], parsed_data[8], parsed_data[9]),

        'Temperature': parsed_data[10],
        'AuxiliaryADC': parsed_data[11]
    }
    return obj

def json_MPU9(message_id, timestamp, parsed_data):
    # This one has not been used
    obj = {
        'fieldID': message_id,
        'timestamp': timestamp,
        'field0': parsed_data[0],
        'field1': parsed_data[1],
        'field2': parsed_data[2],
        'field3': parsed_data[3],
        'field4': parsed_data[4],
        'field5': parsed_data[5],
        'field6': parsed_data[6],
    }
    return obj

def jsonMPL3(message_id, timestamp, parsed_data):
    # This one has not been used
    obj = {
        'fieldID': message_id,
        'timestamp': timestamp,
        'field0': parsed_data[0],
        'field1': parsed_data[1],
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
    
def jsonROLL(message_id, timestamp, parsed_data):
    obj = {
        'fieldID': message_id,
        'timestamp': timestamp,
        'finPosition': parsed_data[0], # servo PWM in microseconds
        'rollServoDisable': parsed_data[1], # boolean
    }
    return obj
    
def magnitude(x, y, z):
    return (x ** 2 + y ** 2 + z ** 2) ** 0.5
