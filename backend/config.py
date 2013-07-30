import datetime
import socket
import sys

# Globals
IP_ADDRESS = ""        # dafault IP
PORT = 35001           # new port used in PSAS server-client example
#PORT = 36000          # old port used in PSAS server-client example
PACKET_SIZE = 4096     # maximum packet size to receive
TIMEOUT = 0.1          # time in seconds to wait for a packet
TIME_RATE = 100000     # the rate of transmitting message to the client's browser 
BAD_DEBUG_ONLY = True  # Show only debug information for bad cases
DEBUG = (sys.argv[1:] == ['-d'])

# packet header
SEQUENCE_LENGTH = 4    # packet sequence field length in bytes

# message header format
FIELD_ID_LENGTH = 4    # message field ID (message type ID) length in bytes
TIMESTAMP_LENGTH = 6   # message timestamp length in bytes
DATA_LENGTH_LENGTH = 2 # message data-length length in bytes
HEADER_LENGTH = \
    FIELD_ID_LENGTH + TIMESTAMP_LENGTH + DATA_LENGTH_LENGTH
FIELD_ID_OFFSET = 0
TIMESTAMP_OFFSET = FIELD_ID_OFFSET + FIELD_ID_LENGTH
DATA_LENGTH_OFFSET = TIMESTAMP_OFFSET + TIMESTAMP_LENGTH
DATA_OFFSET = DATA_LENGTH_OFFSET + DATA_LENGTH_LENGTH
    
# log filename format
LOG_FILE_FORMAT = datetime.datetime.now().strftime("log_%Y.%m.%d_%H-%M-%S")

# this line must be in the end of this file
import debug 
