import time
import thread
import sys

from JSONHandler import createJsonStr, parseJsonStrToObj
from ServerData import ServerData

def attempMaster(sock, address):
  for x in range(0, 3):
    sock.sendto(createJsonStr(204, -1, -1, 0, ''), address)
    time.sleep(2)
    if int(ServerData.myId) != -1:
      break
  if int(ServerData.myId) == -1:
    ServerData.myId = 0
    ServerData.isMaster = True
    ServerData.masterId = 0
    print >>sys.stderr, 'Im now master!'

def heartBeat(sock, serverAddress):
  while True:
    sock.sendto(createJsonStr(202, int(ServerData.myId), ServerData.masterId, 0, ''), serverAddress)
    time.sleep(1)
    if not ServerData.heartBeatAnswered:
      ServerData.attempMaster += 1
    else:
      ServerData.heartBeatAnswered = False
      ServerData.attempMaster = 0
    if ServerData.attempMaster >= 2:
      try:
        thread.start_new_thread(initElectionProcess, (sock,))
      except Exception as e:
        print "Error: unable to start thread for initElectionProcess"
        print(e)
      return
    if int(ServerData.myId) == int(ServerData.masterId):
      return

def initElectionProcess(sock):
  myId = int(ServerData.myId)
  idsToSend = {k: v for k, v in ServerData.servers.items() if int(k) < myId}
  if not idsToSend:
    setMeAsMaster(sock)
  else:
    print >>sys.stderr, 'Start vote process!'
    for key, value in idsToSend.items():
      parts = value.split(':')
      sock.sendto(createJsonStr(206, myId, key, 0, ''), (parts[0], int(parts[1])))
    try:
      thread.start_new_thread(shouldIBeMaster, (sock,))
    except Exception as e:
      print "Error: unable to start thread for shouldIBeMaster"
      print(e)

def setMeAsMaster(sock):
  print >>sys.stderr, 'Im now master!'
  ServerData.isMaster = True
  ServerData.masterId = int(ServerData.myId)
  ServerData.servers.pop(str(ServerData.myId))
  sock.sendto(createJsonStr(203, int(ServerData.myId), 'broadcast', 0, ''), ('255.255.255.255', ServerData.STANDARD_PORT))
  for key, value in ServerData.clients.items():
    parts = value.split(':')
    sock.sendto(createJsonStr(203, int(ServerData.myId), key, 0, ''),(parts[0], int(parts[1])))

def shouldIBeMaster(sock):
  time.sleep(5)
  if ServerData.shouldIBeMaster:
    setMeAsMaster(sock)
  ServerData.shouldIBeMaster = True
