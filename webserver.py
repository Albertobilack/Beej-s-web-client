import socket
import sys
import signal
import re

def signalHandler(sig, frame):
    print("SERVER SHUTDOWN")
    sys.exit(0)

if __name__ == "__main__":

    serverAddress = ('', 28333)
    response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Lenght: 24\r\nConnection: close\r\n\r\nPayload recived, thanks\r\n"
    
    #set custom port for server if provided from command line
    if len(sys.argv) == 2:
        serverAddress[1] = int(sys.argv[1])

    #server setup
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(serverAddress)
    server.listen()

    #client handling
    while True:
        newConnection = server.accept() #tupla socket + return address
        print("connected with IP address: {} | client port number: {}".format(newConnection[1][0], newConnection[1][1]))
        newSocket = newConnection[0]
        header = ""                    #header = b''
        payload = ""
        byteScanned, payloadByteLenght = 0, 0

        while True:
            buffer = newSocket.recv(4096)
            if not buffer:  #disconnection handling
                print("the connection to the client has ended")
                break
            header += buffer.decode("ISO-8859-1")
            if "\r\n\r\n" in header:
                initialPayload = header.split("\r\n\r\n")
                for splits in initialPayload[1:]:   #marginale, in caso payload passe il carattere specifico \r\n\r\n
                    payload += splits
                header = initialPayload[0]
                #search for content lenght
                for headerData in header.split("\r\n"):
                    if "Content Lenght:" in headerData:
                        match = re.search(r'\d+', headerData)
                        if match:
                            payloadByteLenght = int(match.group(0))
                            byteScanned += len(initialPayload[1].encode("ISO-8859-1"))
                            print("byte iniziali: ", byteScanned)
                            print("byte of payload:", payloadByteLenght)
                            break
                        else:
                            print("no payload lenght provided")
                            break
                else:
                    continue
                break

        while True:
            if byteScanned>=payloadByteLenght:
                break
            buffer = newSocket.recv(4096)
            if not buffer:
                print("the connection to the client has ended")
                break
            payload += buffer.decode("ISO-8859-1")


        requestMethod = header.split("/") #there should be a bettere way to do this
        print("method: ", requestMethod[0].lstrip())
        if payload:
            print("payload: ", payload, "\n")
        else:
            print("no payload", "\n")

        #send payload to client and close socket dediated to client 
        newSocket.sendall(response.encode("ISO-8859-1"))
        newSocket.close()

        #shut down server if CTRL + C
        signal.signal(signal.SIGINT, signalHandler)

