import sys, socket, select, json
from utility import formatMessage


def serverSetup(port) -> socket:
    serverAddress = ('', port)
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(serverAddress)
    server.listen()
    return server

def retrivePacket(socket):
    global buffer

    payloadLength = int.from_bytes(buffer[socket][0][:2])
    if len(buffer[socket][0]) >= payloadLength + 2:
        packet = buffer[socket][0][2:payloadLength + 2]
        buffer[socket][0] = buffer[socket][0][payloadLength + 2:]
        return packet.decode()
    return False

def packetHandling(socket, packet):
    global buffer

    packet = json.loads(packet)
    if packet["type"] == "hello":
        buffer[socket][1] = packet["nick"]
        broadcast(formatMessage("join", buffer[socket][1]))
    elif packet["type"] == "chat":                     
        broadcast(formatMessage(packet["type"], buffer[socket][1], packet["message"]))
    else:
        broadcast(formatMessage(packet["type"], buffer[socket][1]))

def addNewUser(socket):
    global buffer, readSocketSet

    newConnection, _ = socket.accept()
    buffer[newConnection] = [b'', ""]
    readSocketSet.add(newConnection)

def removeNewUser(s):
    global buffer, readSocketSet

    s.close()
    readSocketSet.remove(s)
    broadcast(formatMessage("leave", buffer[s][1]))
    buffer.pop(s)

#si potrebbe escludere mittente e far stampare automaticamente messaggio al client stesso
def broadcast(message):
    global readSocketSet, mainSocket

    for user in readSocketSet:
        if user != mainSocket: #not best practice
            byteLen = int.to_bytes(len(message), length=2)
            user.sendall(byteLen + message)

buffer = {}  #socket - [buffer, nick]
mainSocket = None
readSocketSet = set()

def runServer(port):
    global buffer, mainSocket, readSocketSet

    mainSocket = serverSetup(port)
    readSocketSet = {mainSocket}

    while True:
        readyToRead, _, _= select.select(readSocketSet, {}, {})
        for s in readyToRead:
            if s == mainSocket:
                addNewUser(s)
            else:
                buffer[s][0] += s.recv(4096)
                if not buffer[s][0]:
                    removeNewUser(s)
                else:
                    while len(buffer[s][0]) > 1:
                        packet = retrivePacket(s)
                        if not packet:
                            break
                        packetHandling(s, packet)

def usage():
    print("usage: server.py port", file=sys.stderr)

def main(argv):
    try:
        port = int(argv[1])
    except:
        usage()
        return 1

    runServer(port)

if __name__ == "__main__":
    sys.exit(main(sys.argv))