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

##################################################################### ADIS ####
def json_ADIS(message_id, timestamp, data):
    obj = {
        'fieldID': message_id,
        'timestamp': timestamp,
        'PowerSupply': data[0] * json_ADIS.POWER_SUPPLY * MILLI,
            # Range After Conversion: 4.75 V - 5.25 V
            # multiplication makes no sense here; division does
        'GyroscopeX': data[1] * json_ADIS.RATE_GYRO,
        'GyroscopeY': data[2] * json_ADIS.RATE_GYRO,
        'GyroscopeZ': data[3] * json_ADIS.RATE_GYRO,
        'AccelerometerX': data[4] * json_ADIS.ACCELEROMETER * MILLI,
        'AccelerometerY': data[5] * json_ADIS.ACCELEROMETER * MILLI,
        'AccelerometerZ': data[6] * json_ADIS.ACCELEROMETER * MILLI,
        'MagnetometerX': data[7] * json_ADIS.MAGNETOMETER * MILLI,
        'MagnetometerY': data[8] * json_ADIS.MAGNETOMETER * MILLI, 
        'MagnetometerZ': data[9] * json_ADIS.MAGNETOMETER * MILLI,
        'Temperature': data[10] * json_ADIS.TEMPERATURE,
        'AuxiliaryADC': data[11] * json_ADIS.AUX_ADC * MICRO,
    }
    return obj
    
# ADIS fixed to float unit conversion coefficients
json_ADIS.POWER_SUPPLY = float(2.418)  # milli Volts        (mV)
json_ADIS.RATE_GYRO = float(0.05)      # degrees per second (deg/sec)
json_ADIS.ACCELEROMETER = float(3.33)  # milli gee          (mG)
json_ADIS.MAGNETOMETER = float(0.5)    # milli gauss        (mgauss)
json_ADIS.TEMPERATURE = float(0.14)    # degrees in Celsius (deg C)
json_ADIS.AUX_ADC = float(806)         # micro Volts        (mu V)    

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
        'finPosition': data[0], # servo PWM in microseconds
        'rollServoDisable': data[1], # boolean
    }
    return obj
    
def magnitude(x, y, z):
    return (x ** 2 + y ** 2 + z ** 2) ** 0.5
