import threading
import SocketServer
import json
import socket
import time
import sys

_TIME_STEP = 0.00001

class _ChannelData():
    r_s = 0
    r_r = 0
    w_s = 0
    w_r = 0
    r_pre = 0
    w_pre = 0
    lock = threading.Lock()

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
        with c.lock:
            if data[0].endswith("_in"):
                c.w_s, c.w_r, c.w_pre, c.val = data[1], data[2], data[3], data[4]
                if c.r_pre < c.w_pre:
                    c.r_pre, c.r_s, c.r_r = c.w_pre, 0, 0
            elif data[0].endswith("_o"):
                c.r_s, c.r_r, c.r_pre = data[1], data[2], data[3]
                if c.w_pre < c.r_pre:
                    c.w_pre, c.r_s, c.w_r = c.r_pre, 0, 0
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
        self.TIME_OUT = sys.maxint

    def close(self):
        self.server.shutdown()
        self.server.server_close()

    def settimeout(self, s):
        self.TIME_OUT = s

    def _checkPartner(self,name,partner,d,start):
        p = 0
        while not name in d:
            try:
                if(time.time() - start > self.TIME_OUT):
                    return None
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.settimeout(0.1)
                client.connect((self.oip, self.oport))
            except socket.timeout:
                client.close()
                continue
            except socket.error:
                client.close()
                continue
            tosend = json.dumps([partner, 0, 0, p]);
            client.sendall(tosend)
            client.close()
            time.sleep(_TIME_STEP)
            p += 1
        return True

    def _sendStream(self,ip,port,l):
        tosend = json.dumps(l);
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((ip, port))
        client.sendall(tosend)
        client.close()

    def receive(self,name,partner):
        start = time.time()
        name += "_in"
        partner += "_o"
        d = self.server.data
        if not self._checkPartner(name,partner,d,start):
            return None
        c = d[name]
        while True:
            with c.lock:
                if c.r_s < c.w_s:
                    c.r_s = c.w_s
                    c.r_r += 1
                    break
            time.sleep(_TIME_STEP)
            if(time.time() - start > self.TIME_OUT):
                return None
        self._sendStream(self.oip, self.oport, [partner, c.r_s, c.r_r, c.r_pre])
        return c.val

    def send(self,name,partner,value):
        start = time.time()
        name += "_o"
        partner += "_in"
        d = self.server.data
        if not self._checkPartner(name,partner,d,start):
            return False
        c = d[name]
        with c.lock:
            c.w_s += 1
        while True:
            with c.lock:
                if c.w_r < c.r_r:
                    c.w_r = c.r_r
                    self._sendStream(self.oip, self.oport, [partner, c.w_s, c.w_r, c.w_pre])
                    break
            self._sendStream(self.oip, self.oport, [partner, c.w_s, c.w_r, c.w_pre])
            time.sleep(_TIME_STEP)
            if(time.time() - start > self.TIME_OUT):
                return False
        return True
        
    
