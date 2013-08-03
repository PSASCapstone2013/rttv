# modularization part
from config import *
from parsing import *
from averaging import *
from back_to_front import *

# to be modularized

def main():
    thread.start_new_thread(tornadoThread, (0,0))
    receive_packets()
    
def receive_packets():
    log_file = open(LOG_FILE_FORMAT, "a")
    sock = init_socket()
    init_data()
    last_seq = sys.maxint

    # listen socket
    while True:
        message = receive_packet(sock)
        if message == '': # timeout - no packets received during TIMEOUT
            # send_data_to_front_end('') # not sure how to make this one to work here
            continue # get the next packet
        debug.print_char('.') # packet received successfully --> print a dot
        seq, last_seq = check_sequence_number(message, last_seq)
        dump_packet_to_log_file(log_file, message, seq)
        
        # parse messages from the packet
        message = message[SEQUENCE_LENGTH:]
        while len(message) > HEADER_LENGTH: # end of data or message was truncated in its header
            message_id, timestamp, length = parse_message_header(message)
            length = overwrite_length(message_id, length)
            if data_is_truncated(message, length):
                break # skip this message and read the next packet
            data = message[HEADER_LENGTH:length+HEADER_LENGTH] # data bytes
            debug.message_header(message_id, length, timestamp) # print debug message
            json_obj = parse_data(message_id, timestamp, length, data)
            send_data_to_front_end(message_id)
            message = message [HEADER_LENGTH+length:] # select the next message 

def dump_packet_to_log_file(logFile, message, seq):
    # dump packet to log file
    logFile.write(delimiter.pack('SEQN', seq, len(message))) # add packet separator
    logFile.write(message)
    # TODO: need to figure out (define) delimiter format

            
def send_data_to_front_end(message_id):
    endTime = datetime.datetime.now()
    if ((endTime - send_data_to_front_end.startTime).microseconds > TIME_RATE):
        if(no_packet_received()):
            send_json_obj(json_ERRO('ERRO',0,"no packet revceived"))
            print "No packet received"
        else:
            send_json_obj(check_before_send(parse_data.ADIS_mess, message_id))
            send_json_obj(parse_data.last_GPS_mess)
            send_json_obj(parse_data.last_MPL3_mess)
            send_json_obj(parse_data.last_MPU9_mess)
        send_json_obj(check_before_send(parse_data.packet_analyze, 'Analyze'))
        init_data()
    send_data_to_front_end.startTime = datetime.datetime.now()            
send_data_to_front_end.startTime = datetime.datetime.now() #executed at program initialization

if __name__ == "__main__":
    main()
