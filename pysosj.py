import threading
import SocketServer
import json
import socket
import time

_TIME_STEP = 0.00001

class _ChannelData():
    r_s = 0
    r_r = 0
    w_s = 0
    w_r = 0
    r_pre = 0
    w_pre = 0

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
        if data[0].endswith("_in"):
            c.w_s, c.w_r, c.w_pre, c.val = data[1], data[2], data[3], data[4]
        elif data[0].endswith("_o"):
            c.r_s, c.r_r, c.r_pre = data[1], data[2], data[3]
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

    def close(self):
        self.server.shutdown()
        self.server.server_close()

    def receive(self,name,partner):
        name += "_in"
        partner += "_o"
        d = self.server.data
        if not name in d:
            while 1:
                try:
                    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client.settimeout(0.1)
                    client.connect((self.oip, self.oport))
                except socket.timeout:
                    client.close()
                    continue
                tosend = json.dumps([partner, 0, 0, 0]);
                client.sendall(tosend)
                client.close()
                break
            while not name in d:
                pass
        print 2
        c = d[name]
        if c.r_pre != c.w_pre:
            c.r_pre = c.w_pre
        print 3
        while c.r_s == c.w_s:
             time.sleep(_TIME_STEP)
        print 4
        c.r_s = c.w_s
        c.r_r += 1
        tosend = json.dumps([partner, c.r_s, c.r_r, c.r_pre]);

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.oip, self.oport))
        client.sendall(tosend)
        client.close()
        return c.val

    def send(self,name,partner,value):
        pass
    
