import socket


host = '127.0.0.1'
port = 65441

server = ('127.0.0.1', 65435)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host,port))

message = 'abobus'

while message != 'q':
	s.sendto(message.encode('utf-8'), server)
	message = input()

s.close()