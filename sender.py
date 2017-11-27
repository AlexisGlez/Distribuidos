from JSONHandler import createJsonStr
from Blockers import Blockers
from ClientData import ClientData

def send(action, source, to, idMessage, content, sock):
  message = createJsonStr(action, source, to, idMessage, content)
  sent = sock.sendto(message, (ClientData.serverIP, ClientData.SERVER_PORT))

def sender(source, sock):
  action = 0
  message = ''
  to = ''
  idMessage = 1
  while True:
    messageRaw = raw_input()
    if not messageRaw:
      continue
    to = ''
    if messageRaw.startswith('@block'):
      parts = messageRaw.split(' ')
      Blockers.blocks.append(parts[1])
      continue
    elif messageRaw == '@users':
      action = 102
      message = messageRaw[6:]
    elif messageRaw.startswith('@to'):
      action = 101
      parts = messageRaw.split(' ')
      message = messageRaw[5 + len(parts[1]):]
      to = parts[1]
    elif messageRaw == 'exit':
      action = 103
      message = messageRaw
    elif messageRaw == '@weather':
      action = 107
      message = messageRaw
    elif messageRaw.startswith('@tweet'):
      action = 108
      message = messageRaw[6:]
    else:
      action = 100
      message = messageRaw

    send(action, source, to, idMessage, message, sock)
    idMessage += 1
    if action == 103:
      break
