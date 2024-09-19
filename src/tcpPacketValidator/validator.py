import os, re

directory = os.path.abspath("tcp_data")

def ipAddressToByte(address):
    bytestring = b''
    for byte in address.split("."):
        bytestring += int(byte).to_bytes(1, 'big')
    return bytestring
    

def tcpPseudoHEader(file, tcpLenght):
    path = os.path.join(directory, file)
    with open(path, "r") as fp:
        fileContect = fp.read()
        tcpAddress = fileContect.split()
        ipOne, ipTwo = ipAddressToByte(tcpAddress[0]), ipAddressToByte(tcpAddress[1])
        ZERO = b'\x00'
        PCTL = b'\x06'
        return (ipOne + ipTwo + ZERO + PCTL + tcpLenght)


def tcpDataManipulation(file):
    #reading binary data
    path = os.path.join(directory, file)
    with open(path, "rb") as fp:
        tcpData = fp.read()
        tcpLenght = len(tcpData)
        checksum = tcpData[16:18]
        tcpZeroChecksum = tcpData[:16] + b'\x00\x00' + tcpData[18:]
        if len(tcpZeroChecksum) % 2 == 1:
             tcpZeroChecksum += b'\x00'
        return checksum, int.to_bytes(tcpLenght, 2, "big"), tcpZeroChecksum

def computeChecksum(pseudoHeader, tcpData):
    data = pseudoHeader + tcpData
    total, offset = 0, 0
    while offset < len(data):
        word = int.from_bytes(data[offset:offset+ 2], "big")
        total += word
        total = (total & 0xffff) + (total >> 16)
        offset += 2

    return (~total) & 0xffff

def validateChecksum(addrfile, dataFile):
    checksum, tcpLenght, tcpZeroChecksum = tcpDataManipulation(dataFile)
    pseudoHeader = tcpPseudoHEader(addrfile, tcpLenght)
    checksumTwo = computeChecksum(pseudoHeader, tcpZeroChecksum)
    if int.from_bytes(checksum) == checksumTwo:
        print("PASS", end = " ")
    else:
        print("FAIL", end= " ")

    print(int.from_bytes(checksum), " ", checksumTwo)

if __name__ == "__main__":

    for file in os.listdir(directory):
        if file.endswith(".txt"):
            addrfile = file
            dataFile = re.sub(r'_addrs_(\d+).txt', r'_data_\1.dat', file)
            if os.path.exists(os.path.join(directory, dataFile)):
                validateChecksum(addrfile, dataFile)