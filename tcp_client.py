import socket

# target_host = input("Enter the target host: ")
# target_port = int(input("Enter the target port: "))

target_host = "0.0.0.0"
target_port = 12345
#client Object for connection
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connecting client 
client.connect((target_host, target_port))

#Sending data
client.send(b'ABCDEF\n')

#Recieving data
responce = client.recv(4096)

print(responce.decode())

#closing connection
client.close()