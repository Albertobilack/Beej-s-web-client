import sys, socket, select, re, json
from utility import formatMessage


def serverSetup(port) -> socket:
    serverAddress = ('', port)
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(serverAddress)
    server.listen()
    return server

#what if we receive multiple sentence at once?
def retrivePacket(socket):
    global buffer

    payloadLength = int.from_bytes(buffer[socket][0][:2])
    if len(buffer[socket][0]) >= payloadLength + 2: #2 è per i byte che comunicano lunghezza pacchetto
        packet = buffer[socket][0][2:payloadLength + 2]
        buffer[socket][0] = buffer[socket][0][payloadLength + 2:]
        return packet.decode() #devo decoddare solo il pacchetto non tutto il buffer altrimenti sminchio lenght bytes degli altri pacchetti
    
    return False

def newUserHandler(socket):
    global buffer

    newConnection, _ = socket.accept()
    buffer[newConnection] = [b'', ""] #list buffer - string

    return newConnection

#migliorare come escludere mainSocket, è una soluzione temporanea
#escludo joiner quando joina, sender quando senda ecc
def broadcast(onlineUsers, message, mainSocket): 

    for user in onlineUsers:
        if user != mainSocket:
            byteLen = int.to_bytes(len(message), length=2)
            user.sendall(byteLen + message) 

buffer = {}  #socket - [buffer, nick]

def runServer(port):
    global buffer

    mainSocket = serverSetup(port)
    readSocketSet = {mainSocket}

    while True:

        readyToRead, _, _= select.select(readSocketSet, {}, {})

        for s in readyToRead:

            if s == mainSocket:
                readSocketSet.add(newUserHandler(s))

            else:
                buffer[s][0] += s.recv(4096)
                
                if not buffer[s][0]:
                    s.close()
                    readSocketSet.remove(s)
                    broadcast(readSocketSet, formatMessage("leave", buffer[s][1]), mainSocket)
                    buffer.pop(s)

                else:#implementazione giusta sarebbe while retreive new packet, extract packet
                    while len(buffer[s][0]) > 1:
                        packet = retrivePacket(s)
                        if not packet:
                            break
                        packet = json.loads(packet)
                        if packet["type"] == "hello":
                            buffer[s][1] = packet["nick"]
                            broadcast(readSocketSet, formatMessage("join", buffer[s][1]), mainSocket)
                        elif packet["type"] == "chat":                     
                            broadcast(readSocketSet, formatMessage(packet["type"], buffer[s][1], packet["message"]), mainSocket)
                        else:
                            print("eccolo", readSocketSet) 
                            broadcast(readSocketSet, formatMessage(packet["type"], buffer[s][1]), mainSocket)

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