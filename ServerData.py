class ServerData:
  myId = -1
  isMaster = False
  lastId = 0
  masterId = -1
  attempMaster = 0
  heartBeatAnswered = False
  clients = {}
  servers = {}
  STANDARD_PORT = 44610
  shouldIBeMaster = True
  