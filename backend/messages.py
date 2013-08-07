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
    'ADIS':     struct.Struct("<12h"),          # ADIS16405 IMU
    'MPU9':     struct.Struct(">7H"),           # MPU9150 IMU
    'MPL3':     struct.Struct(">2L"),           # MPL3115A2 Pressure Sensor
    'ROLL':     struct.Struct("<HB")            # ROLL computer data
}


def json_GPS_bin1(message_id, timestamp, data):
    obj = {
        'fieldID': message_id,
        'timestamp': timestamp,
        'AgeOfDiff': data[0],                   # seconds (s)
        'NumOfSats': data[1],                   # a number
        'GPSWeek': data[2],                     # a number
        'GPSTimeOfWeek': data[3],               # seconds (s)
        'Latitude': data[4],                    # degrees
        'Longitude': data[5],                   # degrees
        'Height': data[6],                      # meters (m)
        'VNorth': data[7],     # velocity North # meters per second (m/s)
        'VEast': data[8],      # velocity East  # meters per second (m/s)
        'Vup': data[9],        # velocity up    # meters per second (m/s)
        'StdDevResid': data[10],                # meters (m)
        'NavMode': data[11],                    # bit flags
        'ExtendedAgeOfDiff': data[12]           # seconds (s)
    }
    return obj

##################################################################### ADIS ####
def json_ADIS(message_id, timestamp, data):
    obj = {
        'fieldID': message_id,
        'timestamp': timestamp,
        'PowerSupply': data[0] * json_ADIS.POWER_SUPPLY,
        'GyroscopeX': data[1] * json_ADIS.RATE_GYRO,
        'GyroscopeY': data[2] * json_ADIS.RATE_GYRO,
        'GyroscopeZ': data[3] * json_ADIS.RATE_GYRO,
        'AccelerometerX': data[4] * json_ADIS.ACCELEROMETER,
        'AccelerometerY': data[5] * json_ADIS.ACCELEROMETER,
        'AccelerometerZ': data[6] * json_ADIS.ACCELEROMETER,
        'MagnetometerX': data[7] * json_ADIS.MAGNETOMETER,
        'MagnetometerY': data[8] * json_ADIS.MAGNETOMETER, 
        'MagnetometerZ': data[9] * json_ADIS.MAGNETOMETER,
        'Temperature': data[10] * json_ADIS.TEMPERATURE + KELVIN_MINUS_CELSIUS,
        'AuxiliaryADC': data[11] * json_ADIS.AUX_ADC,
    }
    return obj
    
# ADIS fixed to float unit conversion coefficients
json_ADIS.POWER_SUPPLY = 2.418 * MILLI                     # volts (V)
json_ADIS.RATE_GYRO = 0.05                                 # deg/sec
json_ADIS.ACCELEROMETER = 3.33 * MILLI * GFORCE_EQ_X_MPS2  # m/s^2
json_ADIS.MAGNETOMETER = 0.5 * MILLI * GAUSS_EQ_X_TESLA    # tesla (T)
json_ADIS.TEMPERATURE = 0.14                               # Celsius (C)
json_ADIS.AUX_ADC = 806.0 * MICRO                          # volts (V)

##################################################################### MPU9 ####
    
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
    # print "JSON ERRO message was generated."
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
        'finPosition': data[0] * MICRO, # servo PWM in seconds
        'rollServoDisable': data[1], # boolean
    }
    return obj
    
def magnitude(x, y, z):
    return (x ** 2 + y ** 2 + z ** 2) ** 0.5
