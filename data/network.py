#! /usr/bin/python3

import socket
import json
import sys

server_ip = open('data/server_ip').read()[:-1]

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = server_ip
        self.port = 5555
        self.addr = (self.server, self.port)
        self.p = self.connect()

    def getP(self):
        return self.p

    def connect(self):
        try:
            self.client.connect(self.addr)
            return json.loads(self.client.recv(16000))
        except:
            pass

    def send(self, data):
        try:
            self.client.send(json.dumps(data).encode())
            return json.loads(self.client.recv(16000))
        except socket.error as e:
            print(e)


