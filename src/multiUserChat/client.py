import sys, socket, threading
from multiUserChat.utility import formatMessage

def sendMessage(message, client):
    byteLen = len(message).to_bytes
    client.sendall(byteLen + message)

def receiver():
    print("ok")

def userInterface(nick, client):
    sendMessage(formatMessage("hello", nick).encode(), client)

def spawnThreads(nick, client):
    communicationThread = threading.Thread(target = userInterface, args=(nick, client))
    receiverThread = threading.Thread(target = receiver)
    communicationThread.start()
    receiverThread.start()

    return communicationThread, receiverThread

def runClient(nick, address):

    client = socket.socket()
    client.connect(address)

    communication, receiver = spawnThreads(nick, client)
    communication.join()
    receiver.join()

def usage():
    print("usage: client.py nickname ipAddress port", file=sys.stderr)

def main(argv):
    try:
        nick, address = argv[1],  (argv[2], int(argv[3]))
    except:
        usage()
        return 1

    runClient(nick, address)

if __name__ == "__main__":
    sys.exit(main(sys.argv))