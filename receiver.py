import sys

from JSONHandler import parseJsonStrToObj
from Blockers import Blockers
from ClientData import ClientData

def receiver(sock):
  while True:
    data, server = sock.recvfrom(4096)
    message = parseJsonStrToObj(data)
    action = message['action']
    if action == 105:
      continue
    elif action == 100 or action == 101:
      if message['origin'] not in Blockers.blocks:
        print >>sys.stderr, '"%s"' % message['origin'], ": ", '"%s"' % message['payload']
    elif action == 103:
      print >>sys.stderr, 'Client disconnected successfully.'
      break
    elif action == 104:
      print >>sys.stderr, 'Client is now connected to server.'
    elif action == 102 or action == 107 or action == 108:
      print >>sys.stderr, '"%s"' % message['payload']
    elif action == 203:
      ClientData.serverIP = server[0]
      print >>sys.stderr, 'New Server Found!'
    else:
      print >>sys.stderr, 'Invalid message received.'
