import socket

from tornado.websocket import WebSocketHandler

class Broadcaster(object):
    
    _instance = None
        
    @staticmethod
    def get_instance():
        if not Broadcaster._instance:
            Broadcaster._instance = Broadcaster()
        return _instance
    
    @staticmethod
    def broadcast(data):
        b = get_instance()
        for s in b._clients:
            Broadcaster.write_message(s,data)
    
    def __init__(self):
        self._clients = set()

    def add(self, client):
        self._clients.add(client)
        print 'Added client %s' % client

    def remove(self, client):
        self._clients.remove(client)
        print 'Removed client %s' % client

    @staticmethod
    def write_message(client, data):
        client.write_message(data)
        
        

class BroadcasterProxy(WebSocketHandler):
    broadcaster = Broadcaster.get_instance()
    
    def open(self):
        BroadcasterProxy.broadcaster.add(self)

    def on_close(self):
        BroadcasterProxy.broadcaster.remove(self)

