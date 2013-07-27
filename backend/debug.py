from config import *

def messageHeader(fieldID, length, timestamp):
    if DEBUG and not BAD_DEBUG_ONLY:
        print "  %s %2d %.3f" % (fieldID, length, float(timestamp)/1e9),

        
def printChar(char):
    if not (DEBUG and BAD_DEBUG_ONLY):
        return
    # ================================= debug output =================================
    printChar.time_str = datetime.datetime.now().strftime("%H:%M:%S")
    if printChar.time_str_prev <> printChar.time_str:
        if printChar.total > 0:
            print "(%d)" % printChar.total
        printChar.total = 0
        print printChar.time_str, "",
    sys.stdout.write(char)
    printChar.total += 1
    printChar.time_str_prev = printChar.time_str
    # ================================================================================
printChar.total = 0
printChar.time_str = ""
printChar.time_str_prev = ""