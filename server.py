
# AUTHORS:
#  - Carlos Alexis Gonzalez Gomez
#  - Alejandro Velasco Espejo

import socket
import sys
import thread
import json

from JSONHandler import createJsonStr, parseJsonStrToObj
from weather import getWeather
from twitterHandler import postTwitter
from serverThreads import attempMaster, heartBeat
from ServerData import ServerData

def handleClientMessage(address, message, action):
	# Register client
	if action == 104:
		origin = message['origin']
		if origin in ServerData.clients:
			sock.sendto(createJsonStr(106, 'Invalid', message['destiny'], message['id'], 'Invalid User Name'), address)
		else:
			ServerData.clients[origin] = address[0] + ':' + str(address[1])
			# Send ACK
			sock.sendto(createJsonStr(105, message['origin'], message['destiny'], message['id'], message['payload']), address)
	else:
		# Send ACK
		sock.sendto(createJsonStr(105, message['origin'], message['destiny'], message['id'], message['payload']), address)
		# Private message
		if action == 101:
			to = message['destiny']
			for key, gen in ServerData.clients.items():
				if key == to:
					parts = ServerData.clients[to].split(':')
					sock.sendto(data, (parts[0], int(parts[1])))
		# Public message
		elif action == 100:
			origin = message['origin']
			for key, gen in ServerData.clients.items():
				if key != origin:
					parts = ServerData.clients[key].split(':')
					sock.sendto(data, (parts[0], int(parts[1])))
		# Disconnect message
		elif action == 103:
			sock.sendto(data, address)
			ServerData.clients.pop(message['origin'])
		# List users message
		elif action == 102:
			users = ''
			for key, gen in ServerData.clients.items():
				users += key + ', '
			sock.sendto(createJsonStr(102, 'SERVER', message['destiny'], message['id'], users[:-2]), address)
		elif action == 107:
			weather = getWeather()
			gdlWeather = 'Check your internet connection and try again.'
			if weather is not None:
				gdlWeather = 'The wind for GDL is going to have a speed of: ' + weather['query']['results']['channel']['wind']['speed']
			sock.sendto(createJsonStr(107, 'SERVER', message['destiny'], message['id'], gdlWeather), address)
		elif action == 108:
			response = postTwitter(message['origin'] + ': ' + message['payload'])
			sock.sendto(createJsonStr(108, 'SERVER', message['destiny'], message['id'], response), address)

def handleServerMessage(message, action):
	last_address_with_std_port = (address[0], ServerData.STANDARD_PORT)
	# Connect Server
	if action == 204:
		if ServerData.isMaster:
			ServerData.lastId += 1
			ServerData.servers[ServerData.lastId] = address[0] + ':' + str(ServerData.STANDARD_PORT)
			sock.sendto(createJsonStr(205, int(ServerData.myId), ServerData.lastId, message['id'], ''), last_address_with_std_port)
	# OK Server
	if action == 205:
		ServerData.myId = int(message['destiny'])
		ServerData.masterId = message['origin']
		print >>sys.stderr, 'My Id: ', ServerData.myId
		try:
			thread.start_new_thread(heartBeat, (sock, last_address_with_std_port))
		except Exception as e:
			print "Error: unable to start thread for heartbeat"
			print(e)
	# Heart Beat 
	if action == 202:
		if ServerData.isMaster:
			payload = {
				"clients": ServerData.clients,
				"servers": ServerData.servers
			}
			sock.sendto(createJsonStr(201, int(ServerData.myId), message['origin'], message['id'], json.dumps(payload)), last_address_with_std_port)
	# Private Server Message
	if action == 201:
		if not ServerData.isMaster:
			ServerData.heartBeatAnswered = True
			payload = parseJsonStrToObj(message['payload'])
			ServerData.servers = payload['servers']
			ServerData.clients = payload['clients']
			ServerData.lastId = int(max(ServerData.servers, key=int))
	# Election Victory
	if action == 203 and int(message['origin']) != int(ServerData.myId):
		if not ServerData.isMaster:
			ServerData.masterId = message['origin']
			try:
				thread.start_new_thread(heartBeat, (sock, last_address_with_std_port))
			except Exception as e:
				print "Error: unable to start thread for heartbeat"
				print(e)
	# Server Election
	if action == 206 and not ServerData.isMaster:
		if int(ServerData.myId) < int(message['origin']):
			sock.sendto(createJsonStr(207, int(ServerData.myId), message['origin'], message['id'], ''), last_address_with_std_port)
	# Desist From Election
	if action == 207 and not ServerData.isMaster:
		ServerData.shouldIBeMaster = False
		print >>sys.stderr, 'I can\'t be master.'

# UDP Sockets example taken from https://pymotw.com/2/socket/udp.html
# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

# Bind the socket to the port
server_address = ('0.0.0.0', ServerData.STANDARD_PORT)
print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)

try:
	thread.start_new_thread(attempMaster, (sock, ('255.255.255.255', ServerData.STANDARD_PORT)))
except Exception as e:
	print "Error: unable to start thread"
	print(e)

while True:
	print >>sys.stderr, '\nwaiting to receive message'
	data, address = sock.recvfrom(4096)
	print >>sys.stderr, address

	print >>sys.stderr, 'received %s bytes from %s' % (len(data), address)
	print >>sys.stderr, data

	message = parseJsonStrToObj(data)

	action = message['action']

	if 100 <= action < 200 and ServerData.isMaster:
		handleClientMessage(address, message, action)
	elif 200 <= action < 300:
		handleServerMessage(message, action)
