
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
        if DEBUG and not BAD_DEBUG_ONLY:
            print "Timeout:", TIMEOUT, "seconds."
            print "Solution 1: check whether the server is running"
            print "Solution 2: check whether you are using the right port number"
        return ''

def check_sequence_number(message, last_seq):
    # get and check packet sequence number
    seq = int(message[0:SEQUENCE_LENGTH].encode('hex'), 16)             # sequence number (4 bytes)
    
    temp = datetime.datetime.now()
    parse_data.packet_analyze['PacketReceived'] = parse_data.packet_analyze['PacketReceived'] + 1
    packets_lost = check_for_lost_packets(seq, last_seq, parse_data.packet_analyze['latestPacketReceived'], temp)
    parse_data.packet_analyze['PacketLost'].append(packets_lost)	
    parse_data.packet_analyze['latestPacketReceived'] = temp
    
    last_seq = seq
    if DEBUG and not BAD_DEBUG_ONLY:
        print seq, "(0x%.4x)" % seq
    return seq, last_seq

def check_for_lost_packets(seq, last_seq, previous_packet_received, latest_packet_received):
    packets_lost = seq - last_seq - 1
    obj = {}
    if packets_lost > 0:
        if DEBUG and not BAD_DEBUG_ONLY:
            print packets_lost, "packets were lost between", last_seq, "and", seq
        obj = { 
            'From'      : previous_packet_received.strftime('%H%M%S%f'),
            'To'  	: latest_packet_received.strftime('%H%M%S%f'),
            'PacketsLost': packets_lost
        }
    return obj

def parse_message_header(message):
    message_id = message[FIELD_ID_OFFSET:TIMESTAMP_OFFSET]
    timestamp = int(message[TIMESTAMP_OFFSET:DATA_LENGTH_OFFSET].encode('hex'), 16)
    length = int(message[DATA_LENGTH_OFFSET:DATA_OFFSET].encode('hex'), 16) # data section length (in bytes) (2 bytes)            
    # print message_id, FIELD_ID_OFFSET, TIMESTAMP_OFFSET
    # print timestamp, TIMESTAMP_OFFSET, DATA_LENGTH_OFFSET
    # print length, DATA_LENGTH_OFFSET, DATA_OFFSET
    # exit()
    return message_id,timestamp, length
    
def overwrite_length(message_id, length):
    # workaround for flight computer bug which puts wrong data length value into ADIS header
    if message_id == 'ADIS':
        format = message_type.get(message_id)
        new_length = format.size
        return new_length
    return length
    
def data_is_truncated(message, length_expected):
    if len(message) < length_expected + HEADER_LENGTH: # message was truncated in its data
        # sys.stdout.write('t')
        return True
    return False
