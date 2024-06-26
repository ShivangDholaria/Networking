import socket
import threading

# Defining target
target_ip = "0.0.0.0"
target_port = 9998

# Main server code
def main():

    #Server Creatiom
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target_ip, target_port))                           # Binding server to target

    server.listen(5)                                                # Listening for connections
    print(f"[*] Listening on {target_ip} : {target_port}")

    while True:
        client, addr = server.accept()                              # Accepting connections
        print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()

def handle_client(client_socket):
    with client_socket as sock:
        req = sock.recv(1024)
        print(f'[*] Received: {req.decode("UTF-8")}')
        sock.send(b'ACK')

main()