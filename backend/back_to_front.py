import thread

import tornado.ioloop
import tornado.web
import tornado.websocket
import json

open_web_sockets = [] # an array of open websocket connections
open_web_sockets_lock = thread.allocate_lock() # lock used when accessing the
                                               # thread running the Tornado
                                               # code

class FrontEndWebSocket(tornado.websocket.WebSocketHandler):
    def open(self): # appends a new connection to the end of the array of
                    # connections and generates its position in the array 
        open_web_sockets_lock.acquire()
        open_web_sockets.append(self)
        self.list_position = len(open_web_sockets) - 1
        open_web_sockets_lock.release()
    def on_message(self,message):
        pass
    def on_close(self): # closes a connection in the array of connections by
                        # removing it from is position
        open_web_sockets_lock.acquire()
        open_web_sockets.pop(self.list_position)
        open_web_sockets_lock.release()

application = tornado.web.Application([
    (r"/", FrontEndWebSocket),
])

def tornado_thread(arg1, arg2): # defines a thread that runs a Tornado IO loop
                                # that listens to port 8080
    application.listen(8080) # For some OS's and network setups, this line
                             # generates: "Error [10049]: The requested
                             # address is not valid in its context".
    tornado.ioloop.IOLoop.instance().start()
    
# Send JSON object to the front-end application
def send_json_obj(json_obj):
    if bool(json_obj) == False:
        return

    # To decode the JSON objects in Python, use:
    # objDecoded = json.loads(json_obj)
    # print objDecoded['fieldID'], objDecoded['timestamp']
    open_web_sockets_lock.acquire() 
    
    for webSocket in open_web_sockets: # iterates through every open
                                       # connections in the array
        if webSocket is None: #if the connection is null
            print "It is none"

        tornado.ioloop.IOLoop.instance().add_callback(
            webSocket.write_message,
            json.dumps(json_obj)
            ) # creates a write event that will run during the next iteration
              # of the Tornado io loop. The event will send the json object
              # to the front end. For more detailed info, see:
              #   http://www.tornadoweb.org/en/stable/ioloop.html#callbacks-and-timeouts
              #   http://www.tornadoweb.org/en/stable/websocket.html?highlight=websockets#output
              #   http://docs.python.org/2/library/json.html#basic-usage

    open_web_sockets_lock.release()
