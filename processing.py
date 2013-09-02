from config import *

class Message:
    counter = 0
    data = {}

    def __init__(self):
        self.reset()

    def reset(self):
        self.counter = 0
        self.data = {}
        #for key in self.data.keys():
        #    self.data[key] = 0

    def overwrite(self, new_data):
        self.data = new_data
        self.counter += 1

    def average(self, new_data):
        if self.data == {}:
            self.overwrite(new_data)
            return

        self.counter += 1
        for key in new_data.keys():  # do averaging for every single field ...
            if key == 'timestamp' or \
               key == 'fieldID':   # ... except for some fields
                self.data[key] = new_data[key] # copy the most recent value
                continue             # don't do averaging for these fields
            new_value = new_data[key]
            avg_value = self.data[key]
            avg_value = ((avg_value * (self.counter-1) + new_value) /
                         self.counter)
            self.data[key] = avg_value

    def add_other_fields(self):
        self.data['fieldID'] = self.id

    def magnitude(self, x, y, z):
        return (x ** 2 + y ** 2 + z ** 2) ** 0.5
        
class ADIS(Message):
    id = 'ADIS'

    def add_other_fields(self):
        self.data['fieldID'] = self.id
        self.data['GyroscopeMagn'] = \
            self.magnitude(self.data['GyroscopeX'],
                           self.data['GyroscopeY'],
                           self.data['GyroscopeZ'])
        self.data['AccelerometerMagn'] = \
            self.magnitude(self.data['AccelerometerX'],
                           self.data['AccelerometerY'],
                           self.data['AccelerometerZ'])
        self.data['MagnetometerMagn'] = \
            self.magnitude(self.data['MagnetometerX'],
                           self.data['MagnetometerY'],
                           self.data['MagnetometerZ'])

    def convert(self, tokens, timestamp):
        """ converts message data into a python object """
        """ input: tuple containing tokenized raw message fields """
        """ output: python dictionary object with fields in MKS units """
        data = {
            'timestamp': timestamp,
            'PowerSupply': tokens[0] * self.convert.POWER_SUPPLY,
            'GyroscopeX': tokens[1] * self.convert.RATE_GYRO,
            'GyroscopeY': tokens[2] * self.convert.RATE_GYRO,
            'GyroscopeZ': tokens[3] * self.convert.RATE_GYRO,
            'AccelerometerX': tokens[4] * self.convert.ACCELEROMETER,
            'AccelerometerY': tokens[5] * self.convert.ACCELEROMETER,
            'AccelerometerZ': tokens[6] * self.convert.ACCELEROMETER,
            'MagnetometerX': tokens[7] * self.convert.MAGNETOMETER,
            'MagnetometerY': tokens[8] * self.convert.MAGNETOMETER,
            'MagnetometerZ': tokens[9] * self.convert.MAGNETOMETER,
            'Temperature': (tokens[10] * self.convert.TEMPERATURE +
                            KELVIN_MINUS_CELSIUS),
            'AuxiliaryADC': tokens[11] * self.convert.AUX_ADC,
        }
        return data
    convert.POWER_SUPPLY = 2.418 * MILLI                     # volts (V)
    convert.RATE_GYRO = 0.05                                 # deg/sec
    convert.ACCELEROMETER = 3.33 * MILLI * GFORCE_EQ_X_MPS2  # m/s^2
    convert.MAGNETOMETER = 0.5 * MILLI * GAUSS_EQ_X_TESLA    # tesla (T)
    convert.TEMPERATURE = 0.14                               # Celsius (C)
    convert.AUX_ADC = 806.0 * MICRO                          # volts (V)


class GPS1(Message):
    # id = 'GPS\x01'
    id = 'GPS1'

    def convert(self, tokens, timestamp):
        data = {
            'timestamp': timestamp,
            'AgeOfDiff': tokens[0],                   # seconds (s)
            'NumOfSats': tokens[1],                   # a number
            'GPSWeek': tokens[2],                     # a number
            'GPSTimeOfWeek': tokens[3],               # seconds (s)
            'Latitude': tokens[4],                    # degrees
            'Longitude': tokens[5],                   # degrees
            'Height': tokens[6],                      # meters (m)
            'VNorth': tokens[7],     # velocity North # meters per second (m/s)
            'VEast': tokens[8],      # velocity East  # meters per second (m/s)
            'Vup': tokens[9],        # velocity up    # meters per second (m/s)
            'StdDevResid': tokens[10],                # meters (m)
            'NavMode': tokens[11],                    # bit flags
            'ExtendedAgeOfDiff': tokens[12]           # seconds (s)
        }
        return data
        

class ROLL(Message):
    id = 'ROLL'

    def convert(self, tokens, timestamp):
        obj = {
            'timestamp': timestamp,
            'finPosition': tokens[0] * MICRO, # servo PWM in seconds
            'rollServoDisable': float(tokens[1]),    # boolean
        }
        return obj


class MPL3(Message):
    id = 'MPL3'

    def convert(self, tokens):
        data = {
            'field0': tokens[0],
            'field1': tokens[1],
        }
        return data


class MPU9(Message):
    id = 'MPU9'

    def convert(self, tokens):
        data = {
            'field0': tokens[0],
            'field1': tokens[1],
            'field2': tokens[2],
            'field3': tokens[3],
            'field4': tokens[4],
            'field5': tokens[5],
            'field6': tokens[6],
        }
        return data


class ERRO(Message):
    id = 'ERRO'

    def convert(self, timestamp, data):
        obj = {
            'fieldID': 'ERRO',
            'timestamp': timestamp,
            'message': data,
        }
        return obj


class MESG(Message):
    id = 'MESG'

    def convert(self, timestamp, data):
        obj = {
            'fieldID': 'MESG',
            'timestamp': timestamp,
            'message': data,  # string
        }
        return obj


class Stats():
    id = 'Stats'
    last_seq = sys.maxint  # the sequence number of the very last packet

    packets_received_total = 0
    packets_lost_total = 0
    packets_received_recently = 0
    packets_lost_recently = 0
    most_recent_timestamp = 0
    time_last_packet_received = 'never'

    def new_packet_received(self, seq):
        self.check_for_lost_packets(seq)
        self.last_seq = seq
        self.packets_received_total += 1
        self.packets_received_recently += 1
        self.time_last_packet_received = self.get_current_time_string()

    def get_current_time_string(self):
        time_now = datetime.datetime.now()
        return time_now.strftime("%H:%M:%S.") + time_now.strftime("%f")[0]

    def check_for_lost_packets(self, seq):
        difference = seq - self.last_seq
        if difference <= 1:
            return
        packets_lost_now = seq - self.last_seq - 1
        self.packets_lost_total += packets_lost_now
        self.packets_lost_recently += packets_lost_now

    def recent_timestamp(self, timestamp):
        self.most_recent_timestamp = timestamp

    def reset(self):
        self.packets_received_recently = 0
        self.packets_lost_recently = 0

    def get(self):
        obj = {
            'fieldID': 'Stats',
            'PacketsReceivedTotal': self.packets_received_total,
            'PacketsLostTotal': self.packets_lost_total,
            'PacketsReceivedRecently': self.packets_received_recently,
            'PacketsLostRecently': self.packets_lost_recently,
            'MostRecentTimestamp': self.most_recent_timestamp,
            'TimeLastPacketReceived': self.time_last_packet_received,
        }
        return obj


class Messages:
    adis = ADIS()
    gps1 = GPS1()
    roll = ROLL()
    mpl3 = MPL3()
