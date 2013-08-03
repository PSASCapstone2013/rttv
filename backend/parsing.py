
from config import *
from averaging import *

def init_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP_ADDRESS, PORT))
    sock.settimeout(TIMEOUT)
    return sock

def receive_packet(sock):
    # receive packet
    try:
        message = sock.recv(PACKET_SIZE)
        return message
    except socket.timeout:
        return ''

def check_for_lost_packets(seq, last_seq,
                           previous_packet_received, latest_packet_received):
    packets_lost = seq - last_seq - 1
    obj = {}
    if packets_lost > 0:
        # if DEBUG and not BAD_DEBUG_ONLY:
        #     print packets_lost, "packets were lost between", \
        #           last_seq, "and", seq
        obj = { 
            'From': previous_packet_received.strftime('%H%M%S%f'),
            'To': latest_packet_received.strftime('%H%M%S%f'),
            'PacketsLost': packets_lost
        }
    return obj

def parse_message_header(message):
    message_id = message[FIELD_ID_OFFSET:TIMESTAMP_OFFSET]
    timestamp = int( \
        message[TIMESTAMP_OFFSET:DATA_LENGTH_OFFSET].encode('hex'), 16)
    length = int( \
        message[DATA_LENGTH_OFFSET:DATA_OFFSET].encode('hex'), 16)
    # print message_id, FIELD_ID_OFFSET, TIMESTAMP_OFFSET
    # print timestamp, TIMESTAMP_OFFSET, DATA_LENGTH_OFFSET
    # print length, DATA_LENGTH_OFFSET, DATA_OFFSET
    # exit()
    return message_id,timestamp, length
    
def overwrite_length(message_id, length):
    # workaround for wrong data length in ADIS header
    if message_id == 'ADIS':
        format = message_type.get(message_id)
        new_length = format.size
        return new_length
    return length
    
def data_is_truncated(message, length_expected):
    if len(message) < length_expected + HEADER_LENGTH: # truncated message data
        # sys.stdout.write('t')
        return True
    return False


def parse_data(message_id, timestamp, length, data):
    if message_id == 'ERRO': # data contains a string message
        return json_ERRO(message_id, timestamp, data)
    if message_id == 'MESG': # data contains a string message
        if DEBUG and not BAD_DEBUG_ONLY:
            print "MESG:\"" + data + "\""
        return json_MESG(message_id, timestamp, data)

    # parse data
    format = message_type.get(message_id)
    if format == None or len(data) <> format.size: # validate data format
        if DEBUG:
            print "  warning: unable to parse message of type", message_id
        return None # skip this message

    parsed_data = format.unpack(data) # tuple containing parsed data

    if message_id == 'SEQN':
        return None # skip

    elif message_id == 'GPS\x01':
        parse_data.last_GPS_mess = \
            json_GPS_bin1(message_id, timestamp, parsed_data)

    elif message_id == 'ADIS':
        #debug.print_raw_data(data, 2) # 2 bytes per line
        json_obj = json_ADIS(message_id, timestamp, parsed_data)
        debug.ADIS_conversion(data, parsed_data, json_obj)

        # TODO: move this for-loop into a separate function
        for i in ['X', 'Y', 'Z']:
            parse_data.ADIS_mess['Gyroscope' + i] = \
                (json_obj['Gyroscope' + i] + parse_data.ADIS_mess['Gyroscope'+i])
            parse_data.ADIS_mess['Accelerometer' + i] = \
                (json_obj['Accelerometer'+i] +
                 parse_data.ADIS_mess['Accelerometer'+i])
            parse_data.ADIS_mess['Magnetometer' + i] = \
                (json_obj['Magnetometer'+i] +
                 parse_data.ADIS_mess['Magnetometer'+i])
        parse_data.ADIS_count = parse_data.ADIS_count + 1
        parse_data.ADIS_mess = json_obj

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
        
