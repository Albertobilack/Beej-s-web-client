import sys, socket, threading, json
from utility import formatMessage
from chatui import *
import time

def retrivePacket():
    global buffer

    payloadLength = int.from_bytes(buffer[:2])
    if len(buffer) >= payloadLength + 2:
        packet = buffer[2:payloadLength + 2]
        buffer = buffer[payloadLength + 2:]
        return packet.decode()
    return False

def sendMessage(message, client):
    byteLen = int.to_bytes(len(message), length=2)
    client.sendall(byteLen + message)

def printToUser(message):

    match message["type"]:
        case "chat":
            print_message(f"{message["nick"]}: {message["message"]}")
        case "join":
            print_message(f"*** {message["nick"]} has joined the chat")
        case "leave":
            print_message(f"*** {message["nick"]} has left the chat")

def receiver(client):
    global buffer

    while True:
        payload = client.recv(4096)
        if not payload:
            client.close()
            return 0 #non andrebbe fatto in questo modo
        buffer += payload
        while len(buffer) > 1:
            packet = retrivePacket()
            if not packet:
                break
            printToUser(json.loads(packet))
        
def sender(nick, client):

    sendMessage(formatMessage("hello", nick), client)
    while True:
        message = read_command(f"{nick}> ")
        if message.startswith("/"): #si può miglioare
            command = message[1:]
            if command == "q":
                print("Quitting the chat...")
                client.close()
                return 0 #NON CHIUDE IL RECEIVER, QUINDI LA SESSIONE RIMANE APERTA
            else:
                print(f"Unknown command: {command}")
        else:
            sendMessage(formatMessage("chat", nick, message), client)

def runThreads(nick, client):
    communicationThread = threading.Thread(target = sender, args=(nick, client))
    receiverThread = threading.Thread(target = receiver, args=(client,))
    communicationThread.start()
    receiverThread.start()
    communicationThread.join()
    receiverThread.join() #cosa succede se solamente uno dei due ritorna ? il programma non si chiude perché aspetta l'altro

def runClient(nick, address):

    client = socket.socket()
    client.connect(address)

    init_windows()
    runThreads(nick, client)
    end_windows()

def usage():
    
    print("usage: client.py nickname ipAddress port", file=sys.stderr)

buffer = b''

def main(argv):
    try:
        nick, address = argv[1],  (argv[2], int(argv[3]))
    except:
        usage()
        return 1

    runClient(nick, address)

if __name__ == "__main__":
    sys.exit(main(sys.argv))