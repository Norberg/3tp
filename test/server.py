# Echo server program
import socket

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 4242              # Arbitrary non-privileged port
s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
conn, addr = s.accept()
print 'Connected by', addr
while 1:
	data = conn.recv(1024)
	if not data: break
	print data
	if data == "quit\r\n":
		break
	conn.send(data)
conn.close()
