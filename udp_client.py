import socket

target_host = "127.0.0.1"
target_port = 9998

# Client creation
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Sending data
client.sendto(b'Hello from udp client', (target_host, target_port))

#Recieving data
data, addr = client.recvfrom(4096)

print(data.decode())

#closing connection
client.close()