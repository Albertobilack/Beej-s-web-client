#todo: payload handle = The right thing to do would be to look for a
#      Content-Length header and then receive the header plus that many bytes. 

import socket
import sys
import signal
import re

def signalHandler(sig, frame):
    print("SERVER SHUTDOWN")
    sys.exit(0)

if __name__ == "__main__":

    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    if len(sys.argv) == 2:
        #address = ('', sys.argv[1])
        server.bind(('', int(sys.argv[1])))
    else:
        #address = ('', server.bind(28333))
        server.bind(('', 28333))

    #print(server)

    #server.bind(address)

    server.listen()
    while True:
        newConnection = server.accept() #tupla socket + return address
        print("connected with IP address: {} | client port number: {}".format(newConnection[1][0], newConnection[1][1]))
        newSocket = newConnection[0]
        # newSocket.connect(newConnection[1]) non necessario, socket si connette automaticamente
        #request = b''
        request = ""
        byteScanned, payloadByteLenght = 0, 0
        readingPayload = False
        while True:
            if readingPayload and byteScanned>=payloadByteLenght:
                break
            buffer = newSocket.recv(4096)
            if not buffer:
                print("the connection to the client has ended")
                break
            request += buffer.decode("ISO-8859-1")
            if readingPayload:
                byteScanned += len(buffer)
            if "\r\n\r\n" in request and not byteScanned:       #it's possibile to avoid a research in the whole request searching ( i-1Buffer + iBuffer )
                requestData = request.split("\r\n")
                for data in requestData:
                    if "Content Lenght:" in data:
                        match = re.search(r'\d+', data)
                        if match:
                            payloadByteLenght = int(match.group(0))
                            print("byte of payload:", payloadByteLenght)
                            readingPayload = True
                            initialPayload = request.split("\r\n\r\n")
                            byteScanned += len(initialPayload[1].encode("ISO-8859-1"))
                            print("byte iniziali: ", byteScanned)
                            break
                        else:
                            print("no payload lenght provided")

        requestMethod = request.split("/") #there should be a bettere way to do this
        print("method: ", requestMethod[0].lstrip())
        payload = request.split("close\r\n\r\n")
        if payload[1]:
            print("payload: ", payload[1], "\n")
        else:
            print("no payload", "\n")

        response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Lenght: 6\r\nConnection: close\r\n\r\nPayload recived, thanks\r\n"
        newSocket.sendall(response.encode("ISO-8859-1"))
        newSocket.close()
        signal.signal(signal.SIGINT, signalHandler)

