import datetime
import time
import socket
import sys

# global constants
IP_ADDRESS = ""        # dafault IP
PORT = 35001           # new port used in PSAS server-client example
#PORT = 36000          # old port used in PSAS server-client example
PACKET_SIZE = 4096     # maximum packet size to receive
TIMEOUT = 0.1          # backend to frontend update frequency                       

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
GFORCE_EQ_X_MPS2 = 9.80665 # g-force equals 9.81 meters per second squared
GAUSS_EQ_X_TESLA = 0.0001 # gauss equals 0.0001 teslas
KELVIN_MINUS_CELSIUS = 273.0 # (K = C + 273) equivalent to (K - C = 273)

# this line must be in the end of this file
import debug 
