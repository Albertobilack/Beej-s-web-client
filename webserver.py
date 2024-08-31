#todo: payload handle = The right thing to do would be to look for a
#      Content-Length header and then receive the header plus that many bytes. 

import socket
import sys

if __name__ == "__main__":

    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    if len(sys.argv) == 2:
        #address = ('', sys.argv[1])
        server.bind(('', int(sys.argv[1])))
    else:
        #address = ('', server.bind(28333))
        server.bind(('', 28333))

    print(server)

    #server.bind(address)

    server.listen()
    while True:
        newConnection = server.accept() #tupla socket + return address
        #print("NUOVA CONNESSIONE")
        #print(newConnection)
        newSocket = newConnection[0]
        # newSocket.connect(newConnection[1]) non necessario, socket si connette automaticamente
        #request = b''
        request = ""
        while True:
            buffer = newSocket.recv(4096)
            if not buffer:
                print("connessione chiusa")
                break
            request += buffer.decode("ISO-8859-1")
            if "\r\n\r\n" in request:
                break
        #print(request)
        response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Lenght: 6\r\nConnection: close\r\n\r\nHello!\r\n"
        newSocket.sendall(response.encode("ISO-8859-1"))
        newSocket.close()

