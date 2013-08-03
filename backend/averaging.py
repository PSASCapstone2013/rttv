
import datetime
import sys

from messages import *
from config import *

def no_packet_received():
    if((parse_data.ADIS_mess == {}) and \
       (parse_data.last_GPS_mess == {}) and \
       (parse_data.last_MPL3_mess == {}) and \
       (parse_data.last_MPU9 == {})):
        return True
    return False


def check_before_send(json_obj, message_id):
    if (message_id == 'ADIS') :
        for i in ['X', 'Y', 'Z']:
            json_obj['Gyroscope' + i] = \
                (json_obj['Gyroscope' + i]) / parse_data.ADIS_count
            json_obj['Accelerometer' + i] = \
                (json_obj['Accelerometer'+i]) / parse_data.ADIS_count
            json_obj['Magnetometer' + i] = \
                (json_obj['Magnetometer' + i]) / parse_data.ADIS_count

        json_obj['GyroscopeMagn'] = magnitude(json_obj['GyroscopeX'],
                                              json_obj['GyroscopeY'],
                                              json_obj['GyroscopeZ'])
        json_obj['AccelerometerMagn'] = magnitude(json_obj['AccelerometerX'],
                                                  json_obj['AccelerometerY'],
                                                  json_obj['AccelerometerZ'])
        json_obj['MagnetometerMagn'] = magnitude(json_obj['MagnetometerX'],
                                                 json_obj['MagnetometerY'],
                                                 json_obj['MagnetometerZ'])
        init_data()
    if (message_id == 'Analyze'):
        json_obj['latestPacketReceived'] = \
            json_obj['latestPacketReceived'].strftime('%H%M%S%f')
    return json_obj

def init_data():
    parse_data.packet_analyze = init_packet_analyze()
    parse_data.last_GPS_mess = {}
    parse_data.last_MPU9_mess = {}
    parse_data.last_MPL3_mess = {}
    parse_data.ADIS_count = 0
    parse_data.ADIS_mess = {}
    for i in ['X', 'Y', 'Z', 'Magn']:
        parse_data.ADIS_mess['Gyroscope' + i] = 0
        parse_data.ADIS_mess['Accelerometer' + i] = 0
        parse_data.ADIS_mess['Magnetometer' + i] = 0

def init_packet_analyze():
    obj = {
        'fieldID': 'Analyze',
        'PacketReceived': 0,
        'latestPacketReceived': datetime.datetime.now(),
        'PacketLost':[],
    }
    return obj
    

def parse_data(message_id, timestamp, length, data):
    if message_id == 'ERRO': # data contains a string message
        return json_ERRO(message_id, timestamp, data)
    if message_id == 'MESG': # data contains a string message
        if DEBUG:
            print "MESG:\"" + data + "\""
        return json_MESG(message_id, timestamp, data)

    # parse data
    format = message_type.get(message_id)
    if format == None or len(data) <> format.size: # validate data format
        if DEBUG:
            print "  warning: unable to parse message of type", message_id
        return None # skip this message

    parsed_data = format.unpack(data) # tuple containing parsed data
    if DEBUG and not BAD_DEBUG_ONLY:
        print repr(parsed_data) # display all data in one line

    if message_id == 'SEQN':
        return None # skip

    elif message_id == 'GPS\x01':
        parse_data.last_GPS_mess = \
            json_GPS_bin1(message_id, timestamp, parsed_data)

    elif message_id == 'ADIS':
        temp = json_ADIS(message_id, timestamp, parsed_data)
        for i in ['X', 'Y', 'Z']:
            parse_data.ADIS_mess['Gyroscope' + i] = \
                (temp['Gyroscope' + i] + parse_data.ADIS_mess['Gyroscope'+i])
            parse_data.ADIS_mess['Accelerometer' + i] = \
                (temp['Accelerometer'+i] +
                 parse_data.ADIS_mess['Accelerometer'+i])
            parse_data.ADIS_mess['Magnetometer' + i] = \
                (temp['Magnetometer'+i] +
                 parse_data.ADIS_mess['Magnetometer'+i])
        parse_data.ADIS_count = parse_data.ADIS_count + 1
        parse_data.ADIS_mess = temp

    elif message_id == 'MPU9':
        parse_data.last_MPU9_mess = \
            json_MPU9(message_id, timestamp, parsed_data)

    elif message_id == 'MPL3':
        parse_data.last_MPL3_mess = \
            jsonMPL3(message_id, timestamp, parsed_data)
    
    elif message_id == 'ROLL':
        # TODO: Dang, add averaging code here (Bogdan).
        # something = jsonROLL(message_id, timestamp, parsed_data)
        pass
        
