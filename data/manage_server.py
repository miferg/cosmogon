#! /usr/bin/python3
"""
Function definitions for cosmogon to work.
"""

import os
import sys

server = server_ip = open('data/server_ip').read()[:-1]

print('Cosmogon server')
print('The current server adress is: '+ server)
desicion = input('Change it (y/n)? ')

if 'y' in desicion:
    newip = input('Please enter the new server adress: ')
    os.system('echo '+ newip +'> data/server_ip')

server = server_ip = open('data/server_ip').read()[:-1]

desicion = input('Launch a server (y/n)? ')

if 'n' in desicion:
    sys.exit()

print('Server started.')
print('Close this window to stop.')
os.system('data/server.py > server.log')
