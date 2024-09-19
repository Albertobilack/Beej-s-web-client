#GOAL: 
# 1. read tcp address file
# 2. split line in two, source and dest address
# 3. Functions to convert IP address to bytestrings
# 4. Read tcp data file
# 5. function to generate IP pseudo header bytes from the IP address in tcp address file, and the tcp lenght from the tcp data file
# 6. build a new version of the TCP data that has the chedksum set to zero
# 7. concatenate pseudo header and tcp data with zero checksum
# 8. compute the checksum of the concatenation
# 9. extract che checksum from the original data in tcp data
# 10. compare the two checksum

import os
import re

def ipAddressToByte(address):
    bytestring = b''
    for byte in address.split("."):
        bytestring += int(byte).to_bytes(1, 'big')
    return bytestring
    

def tcpPseudoHEader(file, tcpLenght):
    path = os.path.join(os.path.abspath("."), "tcp_data", file)
    with open(path, "r") as fp:
        fileContect = fp.read()
        tcpAddress = fileContect.split()
        ipOne, ipTwo = ipAddressToByte(tcpAddress[0]), ipAddressToByte(tcpAddress[1])
        ZERO = b'\x00'
        PCTL = b'\x06'
        return (ipOne + ipTwo + ZERO + PCTL + tcpLenght)


def tcpDataManipulation(file):
    #reading binary data
    path = os.path.join(os.path.abspath("."), "tcp_data", file)
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
    total = 0
    offset = 0
    while offset < len(data):
        word = int.from_bytes(data[offset:offset+ 2], "big")
        total += word
        total = (total & 0xffff) + (total >> 16)
        offset += 2

    return (~total) & 0xffff

if __name__ == "__main__":

    checksum, tcpLenght, tcpZeroChecksum = tcpDataManipulation("tcp_data_0.dat")
    pseudoHeader = tcpPseudoHEader("tcp_addrs_0.txt", tcpLenght)
    checksumTwo = computeChecksum(pseudoHeader, tcpZeroChecksum)
    if int.from_bytes(checksum) == checksumTwo:
        print("ok")

    print(int.from_bytes(checksum), "\t", checksumTwo)


    # for file in os.listdir(os.path.abspath("tcp_data")):
    #         numbers = re.findall(r'\d+', file)
    #         print(f"Numbers in {file}: {numbers}")