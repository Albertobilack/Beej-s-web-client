import sys
import json
import math
from subnets.netfuncs import *

def dijkstras_shortest_path(routers, srcIp, destIp):
    """
    This function takes a dictionary representing the network, a source
    IP, and a destination IP, and returns a list with all the routers
    along the shortest path.

    The source and destination IPs are **not** included in this path.

    Note that the source IP and destination IP will probably not be
    routers! They will be on the same subnet as the router. You'll have
    to search the routers to find the one on the same subnet as the
    source IP. Same for the destination IP. [Hint: make use of your
    find_router_for_ip() function from the last project!]

    The dictionary keys are router IPs, and the values are dictionaries
    with a bunch of information, including the routers that are directly
    connected to the key.

    This partial example shows that router `10.31.98.1` is connected to
    three other routers: `10.34.166.1`, `10.34.194.1`, and `10.34.46.1`:

    {
        "10.34.98.1": {
            "connections": {
                "10.34.166.1": {
                    "netmask": "/24",
                    "interface": "en0",
                    "ad": 70
                },
                "10.34.194.1": {
                    "netmask": "/24",
                    "interface": "en1",
                    "ad": 93
                },
                "10.34.46.1": {
                    "netmask": "/24",
                    "interface": "en2",
                    "ad": 64
                }
            },
            "netmask": "/24",
            "if_count": 3,
            "if_prefix": "en"
        },
        ...

    The "ad" (Administrative Distance) field is the edge weight for that
    connection.

    **Strong recommendation**: make functions to do subtasks within this
    function. Having it all built as a single wall of code is a recipe
    for madness.
    """

    # distance = for any given node as a key, hold the distance from taht node to the starting node
    # parent = for any given node (as a key) it lists the key for the node that leads back to the 
    # starting node (along the shortes path)

    distance, parent = buildDijkstraTree(routers, srcIp)

    print("distance", distance)
    print()
    print("parent", parent)
    print("---------------------------")

def buildDijkstraTree(routers, srcIp):
    toVisit, distance, parent = initalization(routers, srcIp)

    while toVisit:
        currentNode = findSmallerDistance(toVisit, distance) #current node deve essere key-value con i node che può raggiungere
        toVisit.remove(currentNode)
        for neighbor in routers[currentNode]["connections"]:
            if neighbor in toVisit:
                distanceNeighbor = routers[currentNode]["connections"][neighbor]["ad"] + distance[currentNode] #si può migliorare
                if distanceNeighbor < distance[neighbor]:
                    distance[neighbor] = distanceNeighbor
                    parent[neighbor] = currentNode

    return distance, parent

def findSmallerDistance(toVisit, distance):
    currentNode = ["", math.inf] #node and distance
    for node in toVisit:
        if distance[node] <= currentNode[1]:
            currentNode[0], currentNode[1] = node, distance[node]
    return currentNode[0]

def initalization(routers, srcIp):
    distance = {}
    parent = {}
    toVisit = []
    for node in routers:
        distance[node] = math.inf
        parent[node] = None
        toVisit.append(node)
    distance[find_router_for_ip(routers, srcIp)] = 0
    return toVisit, distance, parent
    

#------------------------------
# DO NOT MODIFY BELOW THIS LINE
#------------------------------
def read_routers(file_name):
    with open(file_name) as fp:
        data = fp.read()

    return json.loads(data)

def find_routes(routers, src_dest_pairs):
    for src_ip, dest_ip in src_dest_pairs:
        path = dijkstras_shortest_path(routers, src_ip, dest_ip)
        print(f"{src_ip:>15s} -> {dest_ip:<15s}  {repr(path)}")
        break #da rimuovere

def usage():
    print("usage: dijkstra.py infile.json", file=sys.stderr)

def main(argv):
    try:
        router_file_name = argv[1]
    except:
        usage()
        return 1

    json_data = read_routers(router_file_name)

    routers = json_data["routers"]
    routes = json_data["src-dest"]

    find_routes(routers, routes)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
    
