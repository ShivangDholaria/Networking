import paramiko

def ssh_cmd(ip, port, user, passwd, cmd):

    # Setting up Paramiko SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy)  # Adds the server's host key automatically to the local 
                                                                # HostKeys object if SSH server is not in the client's known list
    client.connect(ip, port, username=user, password=passwd)

    _, stdout, stderr = client.exec_command(cmd)                # Execute command

    output = stdout.readlines() + stderr.readlines()            # Get output

    if output:
        print('--- OUTPUT ---')
        for line in output:
            print(line.strip())

if __name__ == '__main__':
    import getpass

    user = input('Username: ')                                  # Get username
    password = getpass.getpass()                                # Get password

    ip = input("IP:")                                           # Get IP
    port = int(input("Port:")) or 2222                          # Get port

    cmd = input("Command: ") or 'id'                            # Get command
    ssh_cmd(ip, port, user, password, cmd)
