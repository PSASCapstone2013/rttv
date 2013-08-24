# modularization part
from config import *
from processing import *
from parsing import *
from back_to_front import *
from time import time

stats = Stats()
packet_log = open(PACKET_LOG_FILENAME, "a")

# global objects for data processing
def main():
    debug.open_logs()
    thread.start_new_thread(tornado_thread, (0, 0))
    receive_packets()

def receive_packets():
    global stats
    sock = init_socket()

    # listen socket
    while True:
        new_timeout = data_sync()
        sock.settimeout(new_timeout)
        message = receive_packet(sock)
        if message == '':  # timeout - no packets received during TIMEOUT
            continue  # get the next packet
        if PRINT_CHAR_FOR_ARRIVING_PACKETS:
            debug.print_char('.')  # packet received successfully --> print a dot
        seq = parse_sequence(message)
        stats.new_packet_received(seq)
        dump_packet_to_log_file(message, seq)

        # parse messages from the packet
        message = message[SEQUENCE_LENGTH:]
        while len(message) > HEADER_LENGTH:  # end of data or truncated header
            message_id, timestamp, length = parse_message_header(message)
            stats.recent_timestamp(timestamp)
            length = overwrite_length(message_id, length)
            if data_is_truncated(message, length):
                break  # skip this message and read the next packet
            data = message[HEADER_LENGTH:length + HEADER_LENGTH]  # data bytes
            # debug.message_header(message_id, length, timestamp) # debug message
            parse_data(message_id, timestamp, length, data)
            message = message[HEADER_LENGTH + length:]  # go to next message


def dump_packet_to_log_file(message, seq):
    global packet_log
    # dump packet to log file
    packet_log.write(delimiter.pack('SEQN', seq, len(message)))  # add delimiter
    packet_log.write(message)
    # TODO: need to figure out (define) delimiter format


def data_sync():
    now_time = time()  # in seconds, floating
    if now_time < data_sync.next_update_time:  # not time for an update yet
        # adjust timeout to wait until the next scheduled update time
        return data_sync.next_update_time - now_time
    # otherwise, the update time has just passed, so send an update now.

    if PRINT_CHAR_FOR_BACK_TO_FRONT_UPDATE:
        debug.print_char('U')  # sending JSON data to front-end

    # Sending data update
    send_data_to_front_end_v2()

    data_sync.next_update_time += TIMEOUT  # set new next time for data update
    return max(0, data_sync.next_update_time - time())
    # prevent rare case of negative timeout

# initialize static variables at program start:
data_sync.next_update_time = time() + TIMEOUT


def send_data_to_front_end_v2():
    debug.clear_screen()
    send_ADIS()
    send_ROLL()
    send_GPS1()
    send_stats()
    reset_processing()
    print "\n", "time:  " + stats.get_current_time_string()

def send_ADIS():
    # ADIS, prepare and send
    if Messages.adis.counter > 0:
        Messages.adis.add_other_fields()
        send_json_obj(Messages.adis.data)
        debug.print_ADIS(Messages.adis.data)
        Messages.adis.print_log()
    else:
        print "ADIS:  no data\n\n\n\n\n"

def send_ROLL():
    # ROLL, prepare and send
    if Messages.roll.counter > 0:
        Messages.roll.add_other_fields()
        send_json_obj(Messages.roll.data)
        debug.print_ROLL(Messages.roll.data)
        Messages.roll.print_log()
    else:
        print "ROLL:  no data\n"
        
def send_GPS1():
    # GPS1, prepare and send
    if Messages.gps1.counter > 0:
        Messages.gps1.add_other_fields()
        send_json_obj(Messages.gps1.data)
        debug.print_GPS1(Messages.gps1.data)
        Messages.gps1.print_log()
    else:
        print "GPS1:  no data\n\n\n\n\n\n\n\n\n"

def send_stats():
    global stats
    # Send statistics
    obj = stats.get()
    debug.print_stats(obj)
    send_json_obj(obj)

def reset_processing():
    global stats
    # reset data for the next time chunk
    Messages.adis.reset()
    Messages.roll.reset()
    Messages.gps1.reset()
    stats.reset()
        
if __name__ == "__main__":
    main()
