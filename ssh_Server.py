import paramiko
import sys
import os
import socket
import threading

CWD = os.path.dirname(os.path.realpath(__file__))
HOSTKEY = paramiko.RSAKey(filename=os.path.join(CWD, 'test_key.rsa'))

class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    
    def check_auth_password(self, username, password):
        if username == 'abc' and password ==' 123':
            return paramiko.AUTH_SUCCESSFUL
        
if __name__ == "__main__":
    server = "192.168.1.1"
    ssh_port = 2222

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((server, ssh_port))

        print('[+] Listening for connection...')
        client, addr = sock.accept()
    except Exception as e:
        print(f'[-] Listen failed: {e}')
        sys.exit(1)

    else:
        print(f'[+] Got a connection from {client} on {addr}')

    ssh_sess = paramiko.Transport(client)
    ssh_sess.add_server_key(HOSTKEY)
    server = Server()
    ssh_sess.start_server(server=server)

    chan = ssh_sess.accept(20)

    if chan == None:
        print('[-] No channel.')
        sys.exit(1)
    
    print('[+] Authenticated!')

    print(chan.recv(1024))

    chan.send('Welcome to SSH')

    try:
        while True:
            command = input('Enter command: ').strip('\n')
            if command != 'exit':
                chan.send(command)
                print(chan.recv(8194).decode() + '\n')
            else:
                chan.send('exit')
                print('Exiting...')
                ssh_sess.close()
                break
    except KeyboardInterrupt:
        ssh_sess.close()