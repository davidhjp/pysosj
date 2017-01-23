import threading
import SocketServer
import json
import socket


class _ChannelData():
    r_s = 0
    r_r = 0
    w_s = 0
    w_r = 0


class _Handler(SocketServer.BaseRequestHandler):
    d = ""
    def handle(self):
        while(True):
            data = self.request.recv(1024)
            if not data: 
                break
            else:
                self.d += data
        data = json.loads(self.d)
        if not data[0] in self.server.data:
            self.server.data[data[0]] = _ChannelData()
        c = self.server.data[data[0]] 
        c.r_s, c.r_r = data[1], data[2]
        self.d = ""

class SJInputChannel:
    def __init__(self, ip, port):
        self.ip = ip;
        self.port = port;

    def start(self):
        self.server = SocketServer.TCPServer((self.ip, self.port), _Handler)
        self.server.data = {}
        self.server_t = threading.Thread(target=self.server.serve_forever)
        self.server_t.daemon = True
        self.server_t.start()

    def stop(self):
        self.server_t.shutdown()
        self.server_t.server_close()

    def send(self, data):
        pass
    
