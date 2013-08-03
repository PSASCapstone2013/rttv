
import datetime
import sys

from messages import *
from config import *
from parsing import *

def no_packet_received():
    
    if((parse_data.ADIS_mess['fieldID'] == 'None') and \
       (parse_data.last_GPS_mess == {}) and \
       (parse_data.last_MPL3_mess == {}) and \
       (parse_data.last_MPU9_mess == {})) and \
       (parse_data.last_ROLL_mess['fieldID'] == 'None'):
        return True
    return False


def check_before_send(json_obj, message_id):
    if (message_id == 'ADIS') and (parse_data.ADIS_count > 0) :
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
    if (message_id == 'ROLL') and (parse_data.ROLL_count > 0):
        json_obj['finPosition'] = json_obj['finPosition'] / parse_data.ROLL_count
        if (parse_data.ROLL_true >= parse_data.ROLL_false):
            json_obj['rollServoDisable'] = true
        else:
            json_obj['rollServoDisable'] = false
    return json_obj

def init_data():
    parse_data.packet_analyze = init_packet_analyze()
    parse_data.last_GPS_mess = {}
    parse_data.last_MPU9_mess = {}
    parse_data.last_MPL3_mess = {}
    parse_data.ADIS_count = 0
    parse_data.ADIS_mess = {}
    parse_data.ADIS_mess['fieldID'] = 'None'
    for i in ['X', 'Y', 'Z', 'Magn']:
        parse_data.ADIS_mess['Gyroscope' + i] = 0
        parse_data.ADIS_mess['Accelerometer' + i] = 0
        parse_data.ADIS_mess['Magnetometer' + i] = 0
    parse_data.ROLL_count = 0
    parse_data.last_ROLL_mess = {'fieldID':'None',
                                 'finPosition': 0}
    parse_data.ROLL_true = 0
    parse_data.ROLL_false = 0

def check_sequence_number(message, last_seq):
    # get and check packet sequence number
    seq = int(message[0:SEQUENCE_LENGTH].encode('hex'), 16)

    temp = datetime.datetime.now()
    parse_data.packet_analyze['PacketReceived'] = \
        parse_data.packet_analyze['PacketReceived'] + 1
    packets_lost = check_for_lost_packets( \
        seq, last_seq, parse_data.packet_analyze['latestPacketReceived'], temp)
    parse_data.packet_analyze['PacketLost'].append(packets_lost)
    parse_data.packet_analyze['latestPacketReceived'] = temp
    
    last_seq = seq
    # if DEBUG and not BAD_DEBUG_ONLY:
    #    print seq, "(0x%.4x)" % seq
    return seq, last_seq
        
def init_packet_analyze():
    obj = {
        'fieldID': 'Analyze',
        'PacketReceived': 0,
        'latestPacketReceived': datetime.datetime.now(),
        'PacketLost':[],
    }
    return obj
    
