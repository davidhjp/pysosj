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
        c.w_s, c.w_r = data[1], data[2]
        self.d = ""

class SJChannel:
    def __init__(self, iip, iport, oip, oport):
        self.iip = iip;
        self.iport = iport;
        self.oip = oip;
        self.oport = oport;

        self.server = SocketServer.TCPServer((iip, iport), _Handler)
        self.server.data = {}
        self.server_t = threading.Thread(target=self.server.serve_forever)
        self.server_t.daemon = True
        self.server_t.start()

    def stop(self):
        self.server_t.shutdown()
        self.server_t.server_close()

    def receive(self,name):
        d = self.server.data;
        while not name in d:
            pass
        c = d[name]
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.oip, self.oport))
        client.sendall(++c.r_s)
        client.close()
        while c.w_s != c.r_s:
            pass
        print 123

    
