#! /usr/bin/python3

import socket
from _thread import *
import json
from data import names
import random
import time

# initialize server
server = server_ip = open('server_ip').read()[:-1]
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(2)
print("Waiting for a connection, Server Started")
print(server_ip)

# initialize players
random.shuffle(names)
player1 = {"name":names.pop()}
player2 = {"name":names.pop()}
players = [player1,player2]

# initialize calendar
calorigin = time.perf_counter()

def threaded_client(conn, player):
    #print(json.dumps((players[player],str(calorigin))).encode())
    conn.send(json.dumps((players[player],str(calorigin))).encode())
    reply = ""
    while True:
        try:
            data = json.loads(conn.recv(16000))
            players[player] = data

            if not data:
                print("Disconnected")
                break
            else:
                reply = players
                #print("Received: ", data)
                #print("Sending : ", reply)
            
            conn.sendall(json.dumps(reply).encode())
        except:
            break

    print("Lost connection")
    conn.close()

currentPlayer = 0
while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    start_new_thread(threaded_client, (conn, currentPlayer))
    currentPlayer += 1
