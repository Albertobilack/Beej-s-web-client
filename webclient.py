import socket
import sys

if __name__ == "__main__":

    if len(sys.argv) == 3 :
        address = (sys.argv[1], int(sys.argv[2]))
    else:
        address = (sys.argv[1], 80)

    client = socket.socket()

    client.connect(address)

    request = "GET / HTTP/1.1\r\nHost: %s\r\nConnection: close\r\n\r\n" % (sys.argv[1])

    client.sendall(request.encode("ISO-8859-1"))

    response = b''
    while True:
        buffer = client.recv(4096)
        if not buffer:
            break
        response += buffer
        #buffer = buffer.decode("ISO-8859-1")
    
    client.close()
    
    print(response.decode("ISO-8859-1"))