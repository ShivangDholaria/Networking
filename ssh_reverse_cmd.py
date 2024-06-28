import paramiko
import shlex
import subprocess

def ssh_cmd(ip, port, user, passwd, cmd):

    # Setting up Paramiko SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy)  # Adds the server's host key automatically to the local 
                                                                # HostKeys object if SSH server is not in the client's known list
    client.connect(ip, port=port, username=user, password=passwd)

    ssh_session = client.get_transport().open_session()         # Spinning SSH session with client

    if ssh_session.active:
        ssh_session.send(cmd)                                   # Sending command
        print(ssh_session.recv(1024).decode())
        
        while True:
            command = ssh_session.recv(1024)                    # Receiving command from client

            try:
                cmd = command.decode()

                if cmd == 'exit':                               # Exit check
                    client.close()
                    break
                cmd_output = subprocess.check_output(           # Execute user command
                                        shlex.split(cmd), shell=True) 
                ssh_session.send(cmd_output or 'okay')
            except Exception as e:
                ssh_session.send(str(e))
        client.close()


if __name__ == '__main__':
    import getpass

    user = getpass.getuser()                                    # Get username
    password = getpass.getpass()                                # Get password

    ip = input("IP:")                                           # Get IP
    port = int(input("Port:")) or 2222                          # Get port

    cmd = input("Command: ") or 'id'                            # Get command
    ssh_cmd(ip, port, user, password, 'ClientConnected')        # Sending ClientConnected as initail command to connect with client0
