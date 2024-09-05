import socket, sys, signal, re, os

def signalHandler(sig, frame) -> None:
    print("SERVER SHUTDOWN")
    sys.exit(0)

def payloadHandling() -> int:
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
        return 0
        #sys.exit(0)

def headerHandling(firstLine):
    splitLine = firstLine.split()
    method, path, protocol = splitLine[0], splitLine[1], splitLine[2]
    # method, path, protocol = firstLine.split()[0].lstrip(), firstLine.split()[1].lstrip(), firstLine.split()[2].lstrip()
    print("method:", method)
    print("Path:", path)
    print("protocol:", protocol)
    fileRequested = os.path.split(path)[-1]
    print("file requested:", fileRequested)
    fileExt = os.path.splitext(fileRequested)[-1]
    contentType =  contentTypes.get(fileExt, "application/octet-stream")
    print("tipo di file richiesto:", contentType)

    return method, path, protocol, fileRequested, fileExt, contentType

def readFile(fileRequested):
    try:
        with open(fileRequested, "rb") as fp:
            data = fp.read()
            return data, len(data)
    except FileNotFoundError:
        print("ERROR: File not found")
        return b"", 0
    except Exception as e:
        print("ERROR:", str(e))
        return b"", 0
    except:
        print("ERROR OPENING FILE")

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

def printPayload() -> None :
    if payload:
        print("payload:", payload, "\n")
    else:
        print("no payload", "\n")

contentTypes = {
        ".txt": "text/plain",
        ".html": "text/html",
        ".pdf": "application/pdf",
        ".img": "image/jpeg",
        ".gif": "image/gif"
        }

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
                    payloadByteLenght = payloadHandling()
            elif len(payload) < payloadByteLenght:
                payload += buffer.decode("ISO-8859-1")
            if len(payload) >= payloadByteLenght:
                break

        printPayload()
        headerContainer = header.split("\r\n")
        method, path, protocol, fileRequested, fileExt, contentType = headerHandling(headerContainer[0])
        payloadResponse, contentLenghtResponse = readFile(fileRequested)
        
        response = "%s 200 OK\r\nContent-Type: %s\r\nContent-Lenght: %s\r\nConnection: close\r\n\r\n%s\r\n" % (protocol, contentType, contentLenghtResponse, payloadResponse)

        #send payload to client and close socket dedicated to client 
        newSocket.sendall(response.encode("ISO-8859-1"))
        newSocket.close()

        #shut down server if CTRL + C
        signal.signal(signal.SIGINT, signalHandler)

