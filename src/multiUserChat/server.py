import sys, socket, select, re, json


def serverSetup(port) -> socket:
    serverAddress = ('', port)
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(serverAddress)
    server.listen()
    return server

def receiveData(socket):

    buffer = socket.recv(4096)
    if not buffer:
        return False, None
    return buffer, len(buffer)

def newUserHandler(socket, payload):
    payload = json.loads(payload)   #non necessario, dovrei ricevere direttamente il nome, getsione payload viene fatta prima
    buffer[socket]= '', payload["name"] #da controllare

def formatMessage(type, socket, text):

    match type:
        case "chat":
            message = {"type" : type, "nick": buffer[socket][1], "message": text }
        case "join":
            message = {"type": type, "nick": buffer[socket][1]}
        case "leave":
            message = {"type": type, "nick": buffer[socket][1]}

    return message

#da completare, bisogna aggiungere lendata nei primi 2 byte
def broadcast(onlineUsers, message):

    for user in onlineUsers:
        user.sendall(message.encode()) 

buffer = {} #dict socket - [buffer, nick]

def run_server(port):

    mainSocket = serverSetup(port)
    readSocketSet = {mainSocket}

    while True: 

        readyToRead, _, _= select.select(readSocketSet, {}, {})

        for s in readyToRead:

            if s == mainSocket:
                newConnection = s.accept() #tupla socket + return address
                readSocketSet.add(newConnection[0])

            else:
                data, lenData = receiveData(s) #messaggio.decode

                if True: #sarebbe se è una prima connessione, lo controllo dal "data" guardando se è un hello
                    newUserHandler(s, data) #non è propriamente data da inviare
                    message = formatMessage("join", s)
                    broadcast(readSocketSet, message)

                if not data:
                    s.close()
                    readSocketSet.remove(s)
                    message = formatMessage("leave", s)
                    broadcast(readSocketSet, message)

                else:
                    #datahandling da definire
                    text = "prova"
                    message = formatMessage("chat", readSocketSet, text) #text è "data" inviato dallo user con socket "s"
                    broadcast(readSocketSet, message)

def usage():
    print("usage: server.py port", file=sys.stderr)

def main(argv):
    try:
        port = int(argv[1])
    except:
        usage()
        return 1

    run_server(port)

if __name__ == "__main__":
    sys.exit(main(sys.argv))