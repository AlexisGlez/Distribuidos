import json

def createJsonStr(action, source, to, idMessage, content):
  message = { 'action': action, 'origin': source, 'destiny': to, 'payload': content, 'id': idMessage }
  return json.dumps(message)

def parseJsonStrToObj(jsonStr):
  return json.loads(jsonStr)
