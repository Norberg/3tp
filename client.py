# This Python file uses the following encoding: utf-8
import socket
import random
from server import Server

CRLF = "\r\n"

class Client(Server):

	def __init__(self, name, HOST):
		PORT = 4242
		self.oponentHeader = {}
		self.myHeader = {'version': '1.0', 'name': name,
		                     'user-agent': '3TP/0.1 (Linux 2.6)'}
		self.bord = [[0,0,0],
		             [0,0,0],
		             [0,0,0]]
		self.gameState = "Setup"
		self.turn = 0
		self.conn = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		self.conn.connect((HOST, PORT))
	
		#Send headers to server
		self.sendHeaders()
		#Recive headers from server
		self.reciveHeaders()
		#Start set-play
		print self.turn
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
			if len(self.oponentHeader) >= 4:
				break;
		
	def parseHeader(self, data):
		#parse header	
		if len(self.oponentHeader) < 4 and data != "":
			field = data.partition(":")[0]
			value = data.partition(":")[2]
			if field == "name" or field == "version" or \
			   field == "user-agent" or field == "init": 
	 			self.oponentHeader[field] = value
			if field == "init":
				if int(value) == 0:
			       		self.turn = 1
				elif int(value) == 1:
					self.turn == 0	

	def sendHeaders(self):
		data = ""
		for part in self.myHeader.items():
			data += part[0] + ":" + part[1] + CRLF
		self.conn.send(data)
	
	def printWinner(self):
		winner = self.getWinner()
		if winner == 1:
			print "You won the game"
			self.conn.close()
			quit()
		elif winner == 2:
			print self.oponentHeader["name"], "won the game"
			self.conn.close()
			quit()

			
	def getMarker(self, val):
		if val == 0:
			return " "
		elif val == 1:
			return "☺"
		elif val == 2:
			return "☻"
		else:
			return "?"
		
