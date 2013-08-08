from config import *
import platform

parsing_log = None
def open_logs():
    if not DEBUG:
        return
    global parsing_log
    
    parsing_log_file_name = \
        datetime.datetime.now().strftime("data_validation_log_%Y.%m.%d_%H-%M-%S.txt")
    parsing_log = open(parsing_log_file_name, 'w')
     
def clear_screen():
    if clear_screen.platform == 'Windows':
        os.system('cls')
    else:
        os.system('clear')
clear_screen.platform = platform.system()
     
def message_header(message_id, length, timestamp):
    if DEBUG and not BAD_DEBUG_ONLY:
        print "  %s %2d %.3f" % (message_id, length, float(timestamp) / 1e9),
        
def print_char(char):
    # ============================== debug output =============================
    print_char.time_str = datetime.datetime.now().strftime("%H:%M:%S")
    if print_char.time_str_prev <> print_char.time_str:
        if print_char.total > 0:
            print "(%d)" % print_char.total
        print_char.total = 0
        print print_char.time_str, "",
    sys.stdout.write(char)
    print_char.total += 1
    print_char.time_str_prev = print_char.time_str
    # =========================================================================
print_char.total = 0
print_char.time_str = ""
print_char.time_str_prev = ""

def parsing_message(string):
    if parsing_log == None:
        return
    parsing_log.write(string + '\n')

def print_raw_data(data, bytes_per_line):
    counter = 0
    for byte in data:
        if counter % bytes_per_line == 0:
            print ""
            print "%4d:" % (counter / bytes_per_line),
        counter += 1
        print byte.encode("hex"),
    print ""

def ADIS_conversion(data, parsed_data, obj):
    if parsing_log == None:
        return
        
    parsing_log.write(
        "========================== ADIS ==========================\n")
    parsing_log.write(
        "FIELD            RAW        RAW       CONVERTED      UNITS\n")
    parsing_log.write(
        "description      hex      short        floating           \n")
    parsing_log.write(
        "----------------------------------------------------------\n")
    
    #print "  fieldID:        %15s %15s %10s" % \
    #    (message_id, obj['fieldID'], "" )
    #print "  timestamp:      %15d %15d %10s" % \
    #    (timestamp, obj['timestamp'], "ns")
    
    parsing_log.write("PowerSupply:    %s %10d %15.3f %10s\n" % \
        (data[0:2].encode("hex"), parsed_data[0], obj['PowerSupply'], "V"))

    parsing_log.write("GyroscopeX:     %s %10d %15.3f %10s\n" % \
        (data[2:4].encode("hex"), parsed_data[1], obj['GyroscopeX'], 'deg/sec'))
    parsing_log.write("GyroscopeY:     %s %10d %15.3f %10s\n" % \
        (data[4:6].encode("hex"), parsed_data[2], obj['GyroscopeY'], "deg/sec"))
    parsing_log.write("GyroscopeZ:     %s %10d %15.3f %10s\n" % \
        (data[6:8].encode("hex"), parsed_data[3], obj['GyroscopeZ'], "deg/sec"))
        
    parsing_log.write("AccelerometerX: %s %10d %15.3f %10s\n" % \
        (data[8:10].encode("hex"), parsed_data[4], obj['AccelerometerX'], "m/s^2"))
    parsing_log.write("AccelerometerY: %s %10d %15.3f %10s\n" % \
        (data[10:12].encode("hex"), parsed_data[5], obj['AccelerometerY'], "m/s^2"))
    parsing_log.write("AccelerometerZ: %s %10d %15.3f %10s\n" % \
        (data[12:14].encode("hex"), parsed_data[6], obj['AccelerometerZ'], "m/s^2"))
    
    parsing_log.write("MagnetometerX:  %s %10d %15.9f %10s\n" % \
        (data[14:16].encode("hex"), parsed_data[7], obj['MagnetometerX'], "teslas"))
    parsing_log.write("MagnetometerY:  %s %10d %15.9f %10s\n" % \
        (data[16:18].encode("hex"), parsed_data[8], obj['MagnetometerY'], "teslas"))
    parsing_log.write("MagnetometerZ:  %s %10d %15.9f %10s\n" % \
        (data[18:20].encode("hex"), parsed_data[9], obj['MagnetometerZ'], "teslas"))
        
    parsing_log.write("Temperature:    %s %10d %15.3f %10s\n" % \
        (data[20:22].encode("hex"), parsed_data[10], obj['Temperature'], "deg K"))
        
    parsing_log.write("AuxiliaryADC:   %s %10d %15.9f %10s\n" % \
        (data[22:24].encode("hex"), parsed_data[11], obj['AuxiliaryADC'], "V"))
        
    parsing_log.write(
        "----------------------------------------------------------\n")
        
def valid_ADIS(json_obj):
    global parsing_log
    valid = True
    if not DEBUG or parsing_log == None:
        return True
        
    #if json_obj['fieldID'] <> 'ADIS':
    #    parsing_log.write("ADIS validation: ")
    #    parsing_log.write("%s is not an ADIS id!\n" % \
    #                      json_obj['fieldID'])
    #    valid = False
        
    if json_obj['PowerSupply'] < valid_ADIS.MIN_POWER_SUPPLY:
        parsing_log.write("ADIS validation: ")
        parsing_log.write("PowerSupply = %.3f V is too low!\n" % \
                          json_obj['PowerSupply'])
        valid = False
    if json_obj['PowerSupply'] > valid_ADIS.MAX_POWER_SUPPLY:
        parsing_log.write("ADIS validation: ")
        parsing_log.write("PowerSupply = %.3f V is too high!\n" % \
                          json_obj['PowerSupply'])
        valid = False
        
    for i in ['X', 'Y', 'Z']:
        identifier = 'Gyroscope' + i
        if json_obj[identifier] < valid_ADIS.MIN_GYROSCOPE:
            parsing_log.write("ADIS validation: ")
            parsing_log.write("%s = %.3f deg/sec is too low!\n" % \
                              (identifier, json_obj[identifier]))
            valid = False
        if json_obj[identifier] > valid_ADIS.MAX_GYROSCOPE:
            parsing_log.write("ADIS validation: ")
            parsing_log.write("%s = %.3f deg/sec is too high!\n" % \
                              (identifier, json_obj[identifier]))
            valid = False
            
    for i in ['X', 'Y', 'Z']:
        identifier = 'Accelerometer' + i
        if json_obj[identifier] < valid_ADIS.MIN_ACCELEROMETER:
            parsing_log.write("ADIS validation: ")
            parsing_log.write("%s = %.3f m/s^2 is too low!\n" % \
                              (identifier, json_obj[identifier]))
            valid = False
        if json_obj[identifier] > valid_ADIS.MAX_ACCELEROMETER:
            parsing_log.write("ADIS validation: ")
            parsing_log.write("%s = %.3f m/s^2 is too high!\n" % \
                              (identifier, json_obj[identifier]))
            valid = False
    
    for i in ['X', 'Y', 'Z']:
        identifier = 'Magnetometer' + i
        if json_obj[identifier] < valid_ADIS.MIN_MAGNETOMETER:
            parsing_log.write("ADIS validation: ")
            parsing_log.write("%s = %.3f T is too low!\n" % \
                              (identifier, json_obj[identifier]))
            valid = False
        if json_obj[identifier] > valid_ADIS.MAX_MAGNETOMETER:
            parsing_log.write("ADIS validation: ")
            parsing_log.write("%s = %.3f T is too high!\n" % \
                              (identifier, json_obj[identifier]))
            valid = False

    if json_obj['Temperature'] < valid_ADIS.MIN_TEMPERATURE:
        parsing_log.write("ADIS validation: ")
        parsing_log.write("Temperature = %.3f K is too low!\n" % \
                          json_obj['Temperature'])
        valid = False
    if json_obj['Temperature'] > valid_ADIS.MAX_TEMPERATURE:
        parsing_log.write("ADIS validation: ")
        parsing_log.write("Temperature = %.3f K is too high!\n" % \
                          json_obj['Temperature'])
        valid = False
    
    if json_obj['AuxiliaryADC'] < valid_ADIS.MIN_AUX_ADC:
        parsing_log.write("ADIS validation: ")
        parsing_log.write("AuxiliaryADC = %.9f V is too low!\n" % \
                          json_obj['AuxiliaryADC'])
        valid = False
    if json_obj['AuxiliaryADC'] > valid_ADIS.MAX_AUX_ADC:
        parsing_log.write("ADIS validation: ")
        parsing_log.write("AuxiliaryADC = %.9f V is too high!\n" % \
                          json_obj['AuxiliaryADC'])
        valid = False
    
    
    if not valid:
        return False
    return True

# These values were taken from:
# http://www.analog.com/static/imported-files/data_sheets/ADIS16400_16405.pdf
valid_ADIS.MIN_POWER_SUPPLY  = 4.75    # Volts
valid_ADIS.MAX_POWER_SUPPLY  = 5.25    # Volts
valid_ADIS.MIN_GYROSCOPE     = -300.0  # deg/sec
valid_ADIS.MAX_GYROSCOPE     = 300.0   # deg/sec
valid_ADIS.MIN_ACCELEROMETER = -18.0 * GFORCE_EQ_X_MPS2  # g-force to m/s^2
valid_ADIS.MAX_ACCELEROMETER = 18.0 * GFORCE_EQ_X_MPS2   # g-force to m/s^2
valid_ADIS.MIN_MAGNETOMETER  = -2.5 * GAUSS_EQ_X_TESLA # gauss to tesla (T)
valid_ADIS.MAX_MAGNETOMETER  = 2.5 * GAUSS_EQ_X_TESLA  # gauss to tesla (T)
valid_ADIS.MIN_TEMPERATURE   = -40.0 + KELVIN_MINUS_CELSIUS  # C to K
valid_ADIS.MAX_TEMPERATURE   = 85.0 + KELVIN_MINUS_CELSIUS   # C to K
valid_ADIS.MIN_AUX_ADC       = 0.0     # Volts
valid_ADIS.MAX_AUX_ADC       = 3.3     # Volts

def print_ADIS(obj):
    print ("ADIS: PowerSupply   %.1f V\n" +
           "      Temperature   %.1f K\n" +
           "      AuxiliaryADC  %.9f V\n" +
           "      Gyroscope     %6.3f (%6.3f %6.3f %6.3f) deg/sec\n" +
           "      Accelerometer %6.3f (%6.3f %6.3f %6.3f) m/s^2\n" +
           "      Magnetometer  %9.6f (%9.6f %9.6f %9.6f) teslas") % \
       (obj['PowerSupply'], obj['Temperature'], obj['AuxiliaryADC'], \
        obj['GyroscopeMagn'], \
        obj['GyroscopeX'], obj['GyroscopeY'], obj['GyroscopeZ'], \
        obj['AccelerometerMagn'], \
        obj['AccelerometerX'], obj['AccelerometerY'], obj['AccelerometerZ'],
        obj['MagnetometerMagn'], \
        obj['MagnetometerX'], obj['MagnetometerY'], obj['MagnetometerZ'])
        
def print_ROLL(obj):
    print ("ROLL: finPosition      %6.3f sec\n" +
           "      rollServoDisable %6.3f of truth") % \
          (obj['finPosition'], obj['rollServoDisable'])