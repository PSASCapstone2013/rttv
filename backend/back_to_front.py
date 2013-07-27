import thread

import tornado.ioloop
import tornado.web
import tornado.websocket

openWebSockets = [] #an array of open websocket connections
openWebSocketsLock = thread.allocate_lock() #lock used when accessing the thread running the Tornado code

class FrontEndWebSocket(tornado.websocket.WebSocketHandler):
    def open(self): #appends a new connection to the end of the array of connections and generates its position in the array 
        openWebSocketsLock.acquire()
        openWebSockets.append(self)
        self.list_position = len(openWebSockets) - 1
        openWebSocketsLock.release()
    def on_message(self,message):
        pass
    def on_close(self): #closes a connection in the array of connections by removing it from is position
        openWebSocketsLock.acquire()
        openWebSockets.pop(self.list_position)
        openWebSocketsLock.release()

application = tornado.web.Application([
    (r"/", FrontEndWebSocket),
])

def tornadoThread(arg1, arg2): #defines a thread that runs a Tornado IO loop that listens to port 8080
    application.listen(8080)
    tornado.ioloop.IOLoop.instance().start()
    
# Send JSON object to the front-end application
def sendJsonObj(jsonObj):
    if jsonObj == None:
        return

    # To decode the JSON objects in Python, use:
    # objDecoded = json.loads(jsonObj)
    # print objDecoded['fieldID'], objDecoded['timestamp']
    openWebSocketsLock.acquire() 
    for webSocket in openWebSockets: #iterates through every open connections in the array
        if webSocket is None: #if the connection is null
            print "It is none"
        tornado.ioloop.IOLoop.instance().add_callback(webSocket.write_message, json.dumps(jsonObj)) #creates a write event that will run during the next iteration
                                                                                                    #of the Tornado io loop. The event will send the json object
                                                                                                    #to the front end. See http://www.tornadoweb.org/en/stable/ioloop.html#callbacks-and-timeouts
                                                                                                    #and http://www.tornadoweb.org/en/stable/websocket.html?highlight=websockets#output
                                                                                                    #and http://docs.python.org/2/library/json.html#basic-usage
                                                                                                    #for more detailed info
