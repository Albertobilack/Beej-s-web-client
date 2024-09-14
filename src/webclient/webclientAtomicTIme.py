import socket, time

def system_seconds_since_1900():
    """
    The time server returns the number of seconds since 1900, but Unix
    systems return the number of seconds since 1970. This function
    computes the number of seconds since 1900 on the system.
    """
    # Number of seconds between 1900-01-01 and 1970-01-01
    seconds_delta = 2208988800
    seconds_since_unix_epoch = int(time.time())
    seconds_since_1900_epoch = seconds_since_unix_epoch + seconds_delta
    return seconds_since_1900_epoch 

if __name__ == "__main__":

    address = ("time.nist.gov", 37)

    client = socket.socket()

    client.connect(address)

    payload = ""
    contentLenght = "Content Length: " + str(len(payload))
    contentType = "text/plain"
    request = "GET /  HTTP/1.1\r\nHost: %s\r\n%s\r\n%s\r\nConnection: close\r\n\r\n%s" % ("time.nist.gov", contentType, contentLenght, payload)

    print(request)

    client.sendall(request.encode("ISO-8859-1"))

    response = b''
    while True:
        buffer = client.recv(4096)
        if not buffer:
            break
        response += buffer
    print("response:",response)
    response = int.from_bytes(response)
    client.close()
    
    print(response)
    print(system_seconds_since_1900())