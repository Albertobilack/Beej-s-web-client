import socket
import sys
import signal
import re

def signalHandler(sig, frame) -> None:
    print("SERVER SHUTDOWN")
    sys.exit(0)

def headerHandling() -> int:
    global payload, header

    initialPayload = header.split("\r\n\r\n", 1)
    header = initialPayload[0]
    payload = initialPayload[1]
    match = re.search(r'Content Length:\s*(\d+)', header)
    if match:
        payloadByteLenght = int(match.group(1))
        print("byte iniziali: ", len(payload))
        print("byte of payload:", payloadByteLenght)
        return payloadByteLenght
    else:
        print("no payload lenght provided")
        # sys.exit(0)
        return 0

#socket + port
def portSetup() -> tuple:
    if len(sys.argv) == 2:
        return '', int(sys.argv[1])
    return '', 28333

def serverSetup() -> socket:
    serverAddress = portSetup()
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(serverAddress)
    server.listen()
    return server

response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Lenght: 24\r\nConnection: close\r\n\r\nPayload recived, thanks\r\n"
header = ""
payload = ""

if __name__ == "__main__":

    server = serverSetup()

    #client handling
    while True:

        newConnection = server.accept() #tupla socket + return address
        print("connected with IP address: {} | client port number: {}".format(newConnection[1][0], newConnection[1][1]))
        newSocket = newConnection[0]
        
        payloadByteLenght = -1
        payload, header = "", ""
        while True:
            buffer = newSocket.recv(4096)
            if not buffer:  #client disconnection handling
                print("the connection to the client has ended")
                break
            if payloadByteLenght == -1:
                header += buffer.decode("ISO-8859-1")
                if "\r\n\r\n" in header:
                    payloadByteLenght = headerHandling()
                    if payloadByteLenght == len(payload):
                        break
            elif len(payload) < payloadByteLenght:
                payload += buffer.decode("ISO-8859-1")
            else:
                break

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

