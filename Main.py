import drone_control_functions, time, socket

serverName = '192.168.1.10'	#IP or server hostname
serverPort = 12001	#Port to use

drone_control_functions.setup_IMU_sensor()

while True:
	serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	#(IPv4, TCP)
	serverSocket.connect((serverName, serverPort))	#Connect to server
	serverSocket.send(return_data().encode())	#Send data to 'server'
	message_from_transmitter = serverSocket.recv(1024)
	drone_control_functions.write_to_arduino(int(message_from_transmitter.decode()))
clientSocket.close()	#Close connection
