
from config import *
from processing import *
from back_to_front import *
import socket


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


def parse_sequence(message):
    # get and check packet sequence number
    seq = int(message[0:SEQUENCE_LENGTH].encode('hex'), 16)
    # if DEBUG and not BAD_DEBUG_ONLY:
    #    print seq, "(0x%.4x)" % seq
    return seq


def parse_message_header(message):
    message_id = message[FIELD_ID_OFFSET:TIMESTAMP_OFFSET]
    timestamp = int(message[TIMESTAMP_OFFSET:DATA_LENGTH_OFFSET].encode('hex'), 16)
    length = int(message[DATA_LENGTH_OFFSET:DATA_OFFSET].encode('hex'), 16)
    # print message_id, FIELD_ID_OFFSET, TIMESTAMP_OFFSET
    # print timestamp, TIMESTAMP_OFFSET, DATA_LENGTH_OFFSET
    # print length, DATA_LENGTH_OFFSET, DATA_OFFSET
    # exit()
    return message_id, timestamp, length


def overwrite_length(message_id, length):
    # workaround for wrong data length in ADIS header
    if message_id == 'ADIS':
        format = message_type.get(message_id)
        new_length = format.size
        return new_length
    return length


def data_is_truncated(message, length_expected):
    if len(message) < length_expected + HEADER_LENGTH:  # truncated message data
        # sys.stdout.write('t')
        return True
    return False


def parse_data(message_id, timestamp, length, data):
    if message_id == 'SEQN' or \
       message_id == 'MPL3' or \
       message_id == 'MPU9':
        return  # skip

    if message_id == 'ERRO':  # data contains a string message
        print "ERRO:\"" + data + "\""
        obj = ERRO().convert(timestamp, data)
        send_json_obj(obj)
        return

    if message_id == 'MESG':  # data contains a string message
        print "MESG:\"" + data + "\""
        obj = MESG().convert(timestamp, data)
        send_json_obj(obj)
        return

    # parse messages containing flight data
    format = message_type.get(message_id)
    if format is None or len(data) != format.size:  # validate data format
        debug.parsing_message("Warning: unable to parse message " + message_id)
        return  # skip this message
    # parse date into python tuple containing message fields
    parsed_data = format.unpack(data)

    if message_id == 'ADIS':
        obj = Messages.adis.convert(parsed_data)
        Messages.adis.average(obj)
        if not debug.valid_ADIS(obj):
            #debug.print_raw_data(data, 2) # 2 bytes per line
            debug.ADIS_conversion(data, parsed_data, obj)
        return

    if message_id == 'ROLL':
        obj = Messages.roll.convert(parsed_data)
        Messages.roll.average(obj)
        return

    if message_id == 'GPS\x01' or message_id == 'GPS1':
        obj = Messages.gps1.convert(parsed_data)
        Messages.gps1.overwrite(obj) # store the most recent one only
        return
        
    print "Warning: unknown message id '" + message_id + "'"

    # TODO: GPS1 parsing/processing when actual data is available for testing
    # TODO: MPL3 parsing/processing when PSAS makes it ready
