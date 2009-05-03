# This Python file uses the following encoding: utf-8
import socket
import random

CRLF = "\r\n"

class Server:

	def __init__(self, name):
		HOST = '' #all available interfaces
		PORT = 4242
		self.oponentHeader = {}
		self.myHeader = {'version': '1.0', 'name': name,
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
		#Start mov-play
		self.gamestate = "Mov"
		self.movPlay()

		print self.oponentHeader
		print "Quiting.."
		self.conn.close()

	def reciveHeaders(self):
		while 1:
			data = self.conn.recv(512)
			msg = data.split(CRLF)
			for part in msg:
				self.parseHeader(part)
			#all headers recived
			if len(self.oponentHeader) >= 3:
				break;
		
	def parseHeader(self, data):
		#parse header	
		if len(self.oponentHeader) < 3 and data != "":
			field = data.partition(":")[0]
			value = data.partition(":")[2]
			if field == "name" or field == "version" or \
			   field == "user-agent": 
	 			self.oponentHeader[field] = value

	def sendHeaders(self):
		data = ""
		for part in self.myHeader.items():
			data += part[0] + ":" + part[1] + CRLF
		#randomize player to start
		self.turn =  random.randint(0,1)
		data += "init:" + str(self.turn) + CRLF
		self.conn.send(data)

	def setPlay(self):
		for i in range(6):
			if self.turn == 0: #servers tur
				self.printBord()
				self.printWinner()
				err = 1
				while err != 0:
					pos = raw_input("set >")
					x = pos.partition(",")[0]	
					y = pos.partition(",")[2]
					print "Validateing move..."
					err = self.set(x, y)
					if err != 0:
						print "Invalid action"	
				self.printBord()
				self.printWinner()
				print "Waiting on", self.oponentHeader["name"]
				self.turn = 1	
							
			else: #clients tur
				self.waitOnOponent()
				self.turn = 0

	def set(self, x, y):
		try:
			x = int(x)
			y = int(y)
		except:
			return 5
		self.conn.send("set:" + str(x) + "," + str(y) + CRLF)
		data = self.conn.recv(7)
		data.strip(CRLF)
		field = data.partition(":")[0]
		value = data.partition(":")[2]
		if not value: #if value part missing
		 	return 5
		if field == "err":
			if int(value) == 0:
				self.bord[x-1][y-1] = 1 
			return int(value)
		elif field == "win":
			self.bord[x-1][y-1] = 1 
			return int(0) #win implicit correct move	
			
		else:
			print "Server expected 'err' but got:", data
	
	def movPlay(self):
		while 1:
			if self.turn == 0: #servers tur
				self.printBord()
				self.printWinner()
				err = 1
				while err != 0:
					pos = raw_input("from >")
					fromX = pos.partition(",")[0]	
					fromY = pos.partition(",")[2]
					pos = raw_input("to >")
					toX = pos.partition(",")[0]	
					toY = pos.partition(",")[2]
					print "Validateing move..."
					err = self.mov(fromX, fromY, toX, toY)
					if err != 0:
						print "Invalid action"	
				self.printBord()
				self.printWinner()
				print "Waiting on", self.oponentHeader["name"]
				self.turn = 1	
							
			else: #clients tur
				self.waitOnOponent()
				self.turn = 0

	def mov(self, fromX, fromY, toX, toY):
		fromX = int(fromX)
		fromY = int(fromY)
		toX = int(toX)
		toY = int(toY)
		self.conn.send("mov:" + str(fromX) + "," + str(fromY) + \
			       "→" + str(toX) + "," + str(toY) + CRLF)
		data = self.conn.recv(8)
		data.strip(CRLF)
		field = data.partition(":")[0]
		value = data.partition(":")[2]
		if field == "err":
			if int(value) == 0:
				self.bord[toX-1][toY-1] = 1
	       			self.bord[fromX-1][fromY-1] = 0
			return int(value)
		elif field == "win":
			self.bord[toX-1][toY-1] = 1
	       		self.bord[fromX-1][fromY-1] = 0
			return int(0) #win implicit correct move	
		else:
			print "Server expected 'err' but got:", data

	def waitOnOponent(self):
		data = self.conn.recv(256)
		if self.gamestate == "Set":
			try:
				data.strip(CRLF)
				field = data.partition(":")[0]
				value = data.partition(":")[2]
				x = int(value.partition(",")[0]) - 1
				y = int(value.partition(",")[2]) - 1
			except:
				self.waitOnOponent()
				self.sendError(5)
				return
			if field == "set":
				if x >= 3 or y >= 3: #pos not on border
					self.sendError(2)
					self.waitOnOponent()
					return
				elif self.bord[x][y] == 0: #success
					self.sendError(0)
					self.bord[x][y] = 2
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
		elif self.gamestate == "Mov":
			try:
				data.strip(CRLF)
				field = data.partition(":")[0]
				value = data.partition(":")[2]
				fromPos = value.partition("→")[0]
				toPos = value.partition("→")[2]

				fromX = int(fromPos.partition(",")[0]) - 1
				fromY = int(fromPos.partition(",")[2]) - 1
				toX = int(toPos.partition(",")[0]) - 1
				toY = int(toPos.partition(",")[2]) - 1
			except:
				self.waitOnOponent()
				self.sendError(5)
			if field == "mov":
				#pos not on border
				if fromX >= 3 or fromY >= 3 \
				or toX >= 3 or toY >= 3: 
					self.sendError(2)
					self.waitOnOponent()
					return
				#success
				elif self.bord[toX][toY] == 0 and \
				     self.bord[fromX][fromY] == 2:
					self.sendError(0)
					self.bord[toX][toY] = 2
					self.bord[fromX][fromY] = 0
					return
				#not your marker
				elif self.bord[fromX][fromY] != 2:
					self.sendError(3)
					self.waitOnOponent()
					return
				elif self.bord[toX][toY] != 0:
					self.sendError(4)
					self.waitOnOponent()
					return
					
			#oponent dont follow protokoll
			else:
				self.sendError(5)
				self.waitOnOponent()
				return
			
	def printWinner(self):
		winner = self.getWinner()
		if winner == 1:
			print "You won the game"
			self.conn.send("win:0" + CRLF)
			self.conn.close()
			quit()
		elif winner == 2:
			print self.oponentHeader["name"], "won the game"
			self.conn.send("win:1" + CRLF)
			self.conn.close()
			quit()


	def getWinner(self):
		for player in [1,2]:
			#check vertical
			for i in range(3):
				if self.bord[i][0] == player and \
				   self.bord[i][1] == player and \
				   self.bord[i][2] == player:
				   	return player
			#check horisontal
			for i in range(3):
				if self.bord[0][i] == player and \
				   self.bord[1][i] == player and \
				   self.bord[2][i] == player:
				   	return player
			#check /
			if self.bord[2][0] == player and \
			   self.bord[1][1] == player and \
			   self.bord[0][2] == player:
			   	return player
			#check \
			if self.bord[0][0] == player and \
			   self.bord[1][1] == player and \
			   self.bord[2][2] == player:
				return player

		#no player have won yet
		return 0

	def sendError(self, error):
		self.conn.send("err:" + str(error) + CRLF)

	def printBord(self):
		print "╭─┬─┬─╮"
		for i in range(3):
			print "│" + self.getMarker(self.bord[i][0]) + "│" \
			+ self.getMarker(self.bord[i][1]) + "│" \
			+ self.getMarker(self.bord[i][2]) + "│"
			if i != 2:
				print "├─┼─┼─┤"

		print "╰─┴─┴─╯"

	def getMarker(self, val):
		if val == 0:
			return " "
		elif val == 1:
			return "☻"
		elif val == 2:
			return "☺"
		else:
			return "?"
		
