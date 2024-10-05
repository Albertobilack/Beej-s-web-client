import sys, socket, select, re, json
from multiUserChat.utility import formatMessage


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
    if len(buffer) >= payloadLength + 2: #2 è per i byte che comunicano lunghezza pacchetto
        packet = buffer[2:payloadLength + 2]
        buffer = buffer[payloadLength + 2:]
        return packet.decode() #devo decoddare solo il pacchetto non tutto il buffer altrimenti sminchio lenght bytes degli altri pacchetti
    
    return False

def newUserHandler(socket, payload):
    global buffer

    payload = json.loads(payload)   #non necessario, dovrei ricevere direttamente il nome, getsione payload viene fatta prima
    buffer[socket]= '', payload["name"] #da controllare

#da completare, bisogna aggiungere lendata nei primi 2 byte
def broadcast(onlineUsers, message):

    for user in onlineUsers:
        user.sendall(message.encode()) 

buffer = {}  # dictionary = socket - [buffer, nick]

def runServer   (port):

    mainSocket = serverSetup(port)
    readSocketSet = {mainSocket}

    while True: 

        readyToRead, _, _= select.select(readSocketSet, {}, {})

        for s in readyToRead:

            if s == mainSocket: #new client
                newConnection = s.accept() #tupla socket + return address
                readSocketSet.add(newConnection[0])

            else: #client have data
                buffer[s][0] += (socket.recv(4096))

                if not buffer[s][0]: #client disconnected
                    s.close()
                    readSocketSet.remove(s)
                    broadcast(readSocketSet, formatMessage("leave", buffer[s][1]))                    

                #implementazione giusta sarebbe while retreive new packet, extract packet
                while len(buffer[s][0] >= 1):
                    packet = retrivePacket(s) #dovrei fare due funzioni getnextpacket e extractpacket
                    if not packet:
                        break
                    packet = json.loads(packet)
                    if packet["type"] == "chat":                     
                        broadcast(readSocketSet, formatMessage(packet["type"], buffer[s][1], packet["message"]))
                    else:
                        broadcast(readSocketSet, formatMessage(packet["type"], buffer[s][1]))

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