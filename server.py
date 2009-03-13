import socket
import random

CRLF = "\r\n"

class Server:

	def __init__(self, name):
		print "init"
		HOST = '' # Symbolic name meaning all available interfaces
		PORT = 4242 # Arbitrary non-privileged port
		self.clientHeader = {}
		self.serverHeader = {'version': '1.0', 'name': name,
		                     'user-agent': '3TP/0.1 Linux 2.6'}
		self.bord = [[0,0,0],
		             [0,0,0],
		             [0,0,0]]
		self.gameState = "Setup"
		self.turn = 0
		s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		s.bind((HOST, PORT))
		s.listen(1)
		self.conn, addr = s.accept()
		print 'Connected by', addr
	
		#Recive headers from client
		self.reciveHeaders()
		#Send headers to client
		self.sendHeaders()
		#Start set-play
		self.gamestate = "Set"
		self.setPlay()
		while 1:
			data = self.conn.recv(1024)
			if not data: break
			#self.parse(data)
			if data == "quit\r\n":
				break
			self.conn.send(data)
		print self.clientHeader
		self.conn.close()

	def reciveHeaders(self):
		while 1:
			data = self.conn.recv(512)
			msg = data.split(CRLF)
			for part in msg:
				self.parseHeader(part)
			#all headers recived
			if len(self.clientHeader) >= 3:
				break;
		
	def parseHeader(self, data):
		#parse header	
		if len(self.clientHeader) < 3 and data != "":
			field = data.partition(":")[0]
			value = data.partition(":")[2]
	 		self.clientHeader[field] = value

	def sendHeaders(self):
		data = ""
		for part in self.serverHeader.items():
			data += part[0] + ":" + part[1] + CRLF
		#randomize player to start
		self.turn =  random.randint(0,1)
		data += "init:" + str(self.turn) + CRLF
		self.conn.send(data)

	def setPlay(self):
		for i in range(6):
			if self.turn == 0: #servers tur
				self.printBord()
				pos = raw_input("set >")
				x = pos.partition(",")[0]	
				y = pos.partition(",")[2]
				print "err:", self.set(x, y)
				self.turn = 1	
							
			else: #clients tur
				self.waitOnOponent()
				self.turn = 0

	def set(self, x, y):
		x = int(x)
		y = int(y)
		self.conn.send("set:" + str(x) + "," + str(y) + CRLF)
		data = self.conn.recv(8)
		data.strip(CRLF)
		field = data.partition(":")[0]
		value = data.partition(":")[2]
		if field == "err":
			if int(value) == 0:
				self.bord[x-1][y-1] = 1 
			return int(value)
		else:
			print "Server expected 'err' but got:", data

	def waitOnOponent(self):
		data = self.conn.recv(16)
		if self.gamestate == "Set":
			data.strip(CRLF)
			field = data.partition(":")[0]
			value = data.partition(":")[2]
			x = int(value.partition(",")[0]) - 1
			y = int(value.partition(",")[2]) - 1
			if field == "set":
				if x >= 3 or y >= 3: #pos not on border
					self.sendError(2)
					self.waitOnOponent()
					return
				elif self.bord[x][y] == 0: #success
					self.sendError(0)
					self.bord[x][y] = 2
					if self.markersInGame() == 6:
						self.gamestate = "Mov"
					return
				else: #position busy
					self.sendError(4)
					self.waitOnOponent()
					return
			#oponent dont follow protokoll
			else:
				self.sendError(5)
				self.waitOnOponent()
				return

	def markersInGame(self):
		nr = 0
		for x in self.bord:
			for y in x:
				if y != 0:
					nr += 1
		return nr
	
	def sendError(self, error):
		self.conn.send("err:" + str(error) + CRLF)

	def printBord(self):
		for i in range(9):
			if (self.bord[i/3][i%3] == 1):
				print "X",
			elif (self.bord[i/3][i%3] == 2):
				print "O",
			else:
				print "_",
			if (i % 3 == 0):
				print
