import socket
import pickle

class Network:
    def __init__(self):
        self.client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server="192.168.184.165"
        self.port = 5050
        self.addr=(self.server,self.port)
        self.p=self.connect()

    def getP(self):
        return self.p

    def connect(self):
        try:
            self.client.connect(self.addr)
            return self.client.recv(2048*8).decode()
        except:
            pass

    def send(self,data):
        try:
            self.client.send(str.encode(data))
            return pickle.loads(self.client.recv(2048))
        except EOFError:
            print('An EOFError exception occurred. The file is empty')

