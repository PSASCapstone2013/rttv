import SocketServer, json, sqlite3

conn = sqlite3.connect('rocket.sqlite') #connect to the SQLite database, rocket.sqlite
curs = conn.cursor()

def write_to_database(client_address, json_string):
    """  Writes the ip address and a JSON string to the database table. 
    Automatically gets an index number.
    """
    curs.execute('INSERT INTO rocketdata (ip_addr, json_str) VALUES (?, ?)', (str(client_address[0]), json_string))
    conn.commit()
      
def parse_data(data):
    """ Function to parse the incoming UDP packets.  
    NOTE: Should return dictionary object
    example: return {"gps" : [x, y, z], "name" : "foo", "velocity" : 5434}
    """
    #DO PACKET PARSING HERE
    return {"gps" : [2,5,2], "data" : data} #test values

class MyUDPHandler(SocketServer.BaseRequestHandler):
    """ Creates a handler for the the Python SocketServer to deal with incoming UDP packets.
    """
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]        
        print data #log to file
        json_string = json.dumps(parse_data(data))
        write_to_database(self.client_address, json_string)
        socket.sendto(data.upper(), self.client_address)
        

if __name__ == "__main__":
    import sys
    arg_number = 3
    if(len(sys.argv) != arg_number + 1):
        print "Arg number must be %d." % arg_number
        print "Usage: [host ip address] [port number] [log file path]"
        exit(1)

    try:
        HOST, PORT = sys.argv[1], int(sys.argv[2])
    except ValueError:
        print "Must use number for port number"
        exit(1)
    print "Starting server on %s with port %d. Writing to %s" % (HOST, PORT, sys.argv[3])
    sys.stdout = open(sys.argv[3], "w")
    sys.stderr = sys.stdout
    server = SocketServer.UDPServer((HOST, PORT), MyUDPHandler)
    server.serve_forever()


