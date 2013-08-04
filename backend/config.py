import datetime
import socket
import sys

# global constants
IP_ADDRESS = ""        # dafault IP
PORT = 35001           # new port used in PSAS server-client example
#PORT = 36000          # old port used in PSAS server-client example
PACKET_SIZE = 4096     # maximum packet size to receive
TIMEOUT = 0.1          # time in seconds to wait for a packet
TIME_RATE = 100000     # the rate of transmitting message to the client's browser 

# debugging
BAD_DEBUG_ONLY = False  # Show only debug information for bad cases
DEBUG = (sys.argv[1:] == ['-d'])
PRINT_CHAR_FOR_ARRIVING_PACKETS = True
PRINT_CHAR_FOR_BACK_TO_FRONT_UPDATE = True

# packet header
SEQUENCE_LENGTH = 4    # packet sequence field length in bytes

# message header format
FIELD_ID_LENGTH = 4    # message field ID (message type ID) length in bytes
TIMESTAMP_LENGTH = 6   # message timestamp length in bytes
DATA_LENGTH_LENGTH = 2 # message data-length length in bytes
HEADER_LENGTH = FIELD_ID_LENGTH + TIMESTAMP_LENGTH + DATA_LENGTH_LENGTH
FIELD_ID_OFFSET = 0
TIMESTAMP_OFFSET = FIELD_ID_OFFSET + FIELD_ID_LENGTH
DATA_LENGTH_OFFSET = TIMESTAMP_OFFSET + TIMESTAMP_LENGTH
DATA_OFFSET = DATA_LENGTH_OFFSET + DATA_LENGTH_LENGTH

# log filename format
LOG_FILE_FORMAT = datetime.datetime.now().strftime("log_%Y.%m.%d_%H-%M-%S")

# Unit Conversion
MILLI = 0.001
MICRO = 0.000001
NANO  = 0.000000001
G_FORCE = 9.80665 # meters per second squared

# this line must be in the end of this file
import debug 
