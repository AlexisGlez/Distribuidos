
# AUTHORS:
#  - Carlos Alexis Gonzalez Gomez
#  - Alejandro Velasco Espejo

import socket
import sys
import thread
import time

from JSONHandler import parseJsonStrToObj
from sender import send, sender
from receiver import receiver
from ClientData import ClientData

# Obtener tiempo maquina: time.ctime(time.time())

IP_BROADCAST = '255.255.255.255'

def registerClient(placeHolder):
  userName = raw_input(placeHolder)
  while (' ' in userName) == True:
    userName = raw_input('Spaces are not allowed, Please give me your name: ')
  ClientData.serverIP = IP_BROADCAST
  send(104, userName, '', 0, userName, sock)
  data, server = sock.recvfrom(4096)
  message = parseJsonStrToObj(data)
  if message['action'] == 106:
    return registerClient('This user name already exists in the chat, please enter another one: ')
  return (userName, server)

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

try:
  userName, server = registerClient('What is your name?: ')
  ClientData.serverIP = server[0]
  # Create two threads to handle the send and receive messages
  try:
    thread.start_new_thread(sender, (userName, sock))
    thread.start_new_thread(receiver, (sock,))
  except Exception as e:
    print "Error: unable to start thread"
    print(e)

  while True:
    pass

finally:
    print >>sys.stderr, 'closing socket'
    sock.close()
