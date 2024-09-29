# Example usage:
#
# python select_server.py 3490

import sys, socket, select, re

contentTypes = {
        ".txt": "text/plain",
        ".html": "text/html",
        ".pdf": "application/pdf",
        ".img": "image/jpeg",
        ".gif": "image/gif"
        }

def portSetup() -> tuple:
    # if len(sys.argv) == 2:
    #     return '', int(sys.argv[1])
    # return '', 28333
    return '', int(sys.argv[1])

def serverSetup() -> socket:
    serverAddress = portSetup()
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(serverAddress)
    server.listen()
    return server

def payloadHandling(header, payload) -> int:

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

# def receiveData(socket):

#     payloadByteLenght = -1
#     payload, header = "", ""
#     while True:
#         buffer = socket.recv(4096)
#         if not buffer:  #client disconnection handling
#             return False
#         if payloadByteLenght == -1:
#             header += buffer.decode("ISO-8859-1")
#             if "\r\n\r\n" in header:
#                 payloadByteLenght = payloadHandling(header, payload)
#         elif len(payload) < payloadByteLenght:
#             payload += buffer.decode("ISO-8859-1")
#         if len(payload) >= payloadByteLenght:
#             break

#     return payload, payloadByteLenght

def receiveData(socket):

    buffer = socket.recv(4096)
    if not buffer:
        return False, None
    return buffer, len(buffer)
        

def run_server(port):

    mainSocket = serverSetup()
    #mainSocket = socket.socket()
    #mainSocket.connect(portSetup)
    # mainSocket.listen()

    readSocketSet = {mainSocket}

    while True: 

        readyToRead, _, _= select.select(readSocketSet, {}, {})

        for s in readyToRead:

            if s == mainSocket:
                newConnection = s.accept() #tupla socket + return address
                print(newConnection[1], ": connected")
                readSocketSet.add(newConnection[0])

            else:
                data, lenData = receiveData(s)

                if not data:
                    print(s.getpeername(), ": disconnected")
                    s.close()
                    readSocketSet.remove(s)

                else:
                    print(s.getpeername(), lenData, "bytes:", data )

def usage():
    print("usage: select_server.py port", file=sys.stderr)

def main(argv):
    try:
        port = int(argv[1])
    except:
        usage()
        return 1

    run_server(port)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
