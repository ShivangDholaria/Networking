import sys
import socket
import threading

# TODO -    1. implement request handler
#           2. implement responce handler

# Printable ASCII character from the HEX data 
# Prints character if character is printable else a '.'
HEX_FILTER = ''.join([(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)])      

# Printing the hex dump of traffic
# Prints both hex and its corresponding ASCII values
def hexdump(src, length=16, show=True):
    
    # Byte stream check
    if isinstance(src, bytes):
        src = src.decode()
    
    results = list()
    for i in range(0, len(src), length):
        word = str(src[i:i+length])

        printable = word.translate(HEX_FILTER)                          # Getting all the printable character from the data stream
        hexa = ' '.join([f'{ord(c):02X}' for c in word])                # Getting the hex value of the data stream for each character
        hex_width = length * 3

        results.append(f'{i:04x} {hexa:<{hex_width}} {printable}')
    
    if show:
        for l in results:
            print(l)
    else:
        return results
    
# Recieve data stream from source
def recieve_from(conn):
    buffer = b""                                # Empty buffer to store data 

    conn.settimeout(5)                          # Default timeout time for the connection

    try:
        while True:
            data = conn.revc(4096)
            if not data:
                break
            buffer += data
    except Exception as e:
        pass

    return buffer

# Request handler
def req_handler(buffer):
    return buffer

# Responce handler
def res_handler(buffer):
    return buffer

# Basic proxy handler
def proxy_handler(client_sock, remote_host, remote_port, recieve_first):
    
    # Creating remote socket and connecting to it
    remote_sock = socket,socket(socket.AF_INET, socket.SOCK_STREAM) 
    remote_sock.connect((remote_host, remote_port))

    # Check if our side is not first to send data
    if recieve_first:
        remote_buf = recieve_from(remote_sock)
        hexdump(remote_buf)

    remote_buf = res_handler(remote_buf)

    if len(remote_buf):
        print("[<==] Sending %d bytes to localhost." %len(remote_buf))
        client_sock.send(remote_buf)

    while True:
        local_buf = recieve_from(client_sock)
        if len(local_buf):
            print("[==>] Received %d bytes from localhost." %len(local_buf))
            hexdump(local_buf)
            
            local_buf = req_handler(local_buf)
            remote_sock.send(local_buf)
            print("[==>] Sent to remote.")

        remote_buf = recieve_from(remote_sock)
        if len(remote_buf):
            print("[<==] Received %d bytes from remote." %len(remote_buf))
            hexdump(remote_buf)

            remote_buf = res_handler(remote_buf)
            client_sock.send(remote_buf)
            print("[<==] Sent to localhost.")

        if not len(local_buf) or not len(remote_buf):
            client_sock.close()
            remote_sock.close()
            print("[*] No more data. Closing connections.")
            break

# Server loop
def server_loop(l_host, l_port, r_host, r_port, recieve_first):

    # Creating and binding server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((l_host, l_port))
    except Exception as e:
        print('Problem on bind: %r' %e)

        print(f"[!!] Failed to listen on {l_host}:{l_port}")
        print(f"[!!] Check for other listening sockets or correct permissions.")
        print(f"[!!] {e}")
        sys.exit(0)
    
    print("[*] Listening on %s:%d"%(l_host, l_port))
    server.listen(5)

    while True:
        client_sock, addr = server.accept()
        print(f"> Received incoming connection from {addr[0]}:{addr[1]}")
        
        proxy_thread = threading.Thread(
            target=proxy_handler,
            args=(client_sock, r_host, r_port, recieve_first)
        )

        proxy_thread.start()

def main():
    if len(sys.argv[1:]) != 5:
        print("Usage: ./txp_proxy.py [local_host] [local_port]", end='')
        print("[remote_host] [remote_port] [recieve_first]")
        print("Example: ./tcp_proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(0)
    
    l_host = sys.argv[1]
    l_port = int(sys.argv[2])

    r_host = sys.argv[3]
    r_port = int(sys.argv[4])

    recieve_first = sys.argv[5]

    if "True" in recieve_first:
        recieve_first = True
    else:
        recieve_first = False
    
    server_loop(l_host, l_port, r_host, r_port, recieve_first)

if __name__ == "__main__":
    main()

# hexdump("hello boiz, wassups", 8)