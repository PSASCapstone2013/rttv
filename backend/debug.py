from config import *

def message_header(message_id, length, timestamp):
    if DEBUG and not BAD_DEBUG_ONLY:
        print "  %s %2d %.3f" % (message_id, length, float(timestamp)/1e9),
        
def print_char(char):
    if not (DEBUG and BAD_DEBUG_ONLY):
        return
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