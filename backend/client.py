# modularization part
from config import *
from processing import *
from parsing import *
from back_to_front import *
from time import time

stats = Stats()


# global objects for data processing
def main():
    debug.open_logs()
    thread.start_new_thread(tornado_thread, (0, 0))
    receive_packets()


def receive_packets():
    global stats
    log_file = open(LOG_FILE_FORMAT, "a")
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
        dump_packet_to_log_file(log_file, message, seq)

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


def dump_packet_to_log_file(log_file, message, seq):
    # dump packet to log file
    log_file.write(delimiter.pack('SEQN', seq, len(message)))  # add delimiter
    log_file.write(message)
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
    global stats
    debug.clear_screen()

    # ADIS, prepare and send
    if Messages.adis.counter > 0:
        Messages.adis.add_other_fields()
        send_json_obj(Messages.adis.data)
        debug.print_ADIS(Messages.adis.data)
    else:
        print "ADIS:  no data.\n\n\n\n\n"

    # ROLL, prepare and send
    if Messages.roll.counter > 0:
        Messages.roll.add_other_fields()
        send_json_obj(Messages.roll.data)
        debug.print_ROLL(Messages.roll.data)
    else:
        print "ROLL:  no data.\n"

    # Send statistics
    obj = stats.get()
    debug.print_stats(obj)
    send_json_obj(obj)

    # reset data for the next time chunk
    Messages.adis.reset()
    Messages.roll.reset()
    stats.reset()

    print "\n", "time:  " + stats.get_current_time_string()

if __name__ == "__main__":
    main()
