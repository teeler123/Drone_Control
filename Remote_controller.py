import socket, time, pygame

serverPort = 12001	#Port to use
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	#(IPv4, TCP)
serverSocket.bind(('',serverPort))	#Assigns port number to server socket
serverSocket.listen(1)	#Listen for connection (number of queued connections - at least 1)
print('The controller is ready...')
while True:
	mess_to_send = input('Send: ')
	connectionSocket, clientAddress = serverSocket.accept()	#Create socket called connectionSocket and store client IP in clientAddress
	connectionSocket.send(mess_to_send.encode())
	message_from_veh = connectionSocket.recv(1024).decode()	#Decode the message from client
	print(message_from_veh)
	connectionSocket.close()	#Closes connectionSocket but not serverSocket so more connections can be made