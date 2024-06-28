import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading

# Execute the commands
def execute(cmd):
    cmd = cmd.strip()

    if not cmd:
        return
    # Fire user command 
    output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
    return output.decode()

class NetCat:
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Entry point for execution
    def run(self):
        if self.args.listen:
            self.listen()
        else:
            self.send()
    
    # Send commands
    def send(self):
        self.socket.connect((self.args.target, self.args.port))

        # Sending payload if present
        if self.buffer:
            self.socket.send(self.buffer)  

        # User interuption Handling
        try:
            #Recieve data
            while True:
                recv_len = 1
                responce = ''
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    responce += data.decode()

                    if recv_len < 4096:                 # Break if no more data
                        break

                # Sending data back to user
                if responce:
                    print(responce)
                    buffer = input('> ')
                    buffer += '\n'
                    self.socket.send(buffer.encode())

        except KeyboardInterrupt:
            print("User Terminated the session.\nExiting...")
            self.socket.close()
            sys.exit()
    
    # Listner
    def listen(self):
        # Binding and listening 
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)

        while True:
            client_socket, _ = self.socket.accept()
            client_thread = threading.Thread(
                                    target=self.handle,
                                    args=(client_socket,)
                                            )
            client_thread.start()

    # handler - for command execution, file upload and create interactive shell
    def handle(self, client_socket):

        #Command execution
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode())

        # File upload
        elif self.args.upload:
            file_buf = b''

            # Getting all data from sender and storing it
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buf += data
                else:
                    break
            
            # Writing the data into specified file
            with open(self.args.upload, 'wb') as file:
                file.write(file_buf)
            
            message = f'Saved file {self.args.upload}'
            client_socket.send(message.encode())

        # pop Interactive shell
        elif self.args.command:
            cmd_buf = b''
            while True:
                try:
                    client_socket.send(b'user_shell#> ')
                    while '\n' not in cmd_buf.decode():
                        cmd_buf += client_socket.decode(64)
                    responce = execute(cmd_buf.decode())
                    if responce:
                        client_socket.send(responce.encode())
                    cmd_buf = b''
                except Exception as e:
                    print(f'session terminated {e}')
                    self.socket.close()
                    sys.exit()


# Command line handler
def main():
    # User interface set-up
    parser = argparse.ArgumentParser(description='Netcat tool', 
                                    formatter_class=argparse.RawDescriptionHelpFormatter,
                                    epilog=textwrap.dedent('''Example:
        netcat.py -t 192.168.1.108 -p 5555 -l -c                        # command shell
        netcat.py -t 192.168.1.108 -p 5555 -l -u=mytest.txt             # Upload to file
        netcat.py -t 192.168.1.108 -p 5555 -l -e=\"cat /etc/passwd\"    # Execute shell
        echo 'hello' | netcat.py -t 192.168.1.108 -p 5555               # Echo text to server at specified port
        netcat.py -t 192.168.1.108 -p 5555                              # Connect to server
                                    ''')
                                    )

    # Adding arguements for better functionality
    parser.add_argument('-c', '--command', action='store_true', help='command shell')               # Set up interactive shell
    parser.add_argument('-e', '--execute', help='execute specified command')                        # execute specific command
    parser.add_argument('-l', '--listen', action='store_true', help='listen')                       # Set up listner
    parser.add_argument('-p', '--port', type=int, default=5555, help='specified port')              # specify target port
    parser.add_argument('-t', '--target', default='192.168.1.108', help='specified IP')             # specify target ip
    parser.add_argument('-u', '--upload', help='upload file')                                       # upload specific file

    args = parser.parse_args()

    if args.listen:
        buffer = ''
    else:
        buffer = sys.stdin.read()

    nc = NetCat(args, buffer.encode())
    nc.run()


main()