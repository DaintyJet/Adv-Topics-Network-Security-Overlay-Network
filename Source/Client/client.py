# Import library for timestamps 
from datetime import datetime
# Import threading libraries 
from threading import *  
# Import sleep from time
from time import sleep
# Import socket for network functionality
import socket
# Import the jason library for serializing and deserializing data
import json
# Import sys for command line arguments 
import sys

NetPort = 9999

# This is not waiting the approprate amount of time, this is a known issue, currently for testing
def client_Driver(hostname, netIP, Key):
    clients = flow2_Get_Online(hostname, netIP, Key)
    sleep(5)
    for x in range(0,len(clients), 2):
            flow3_Ping(clients[x], clients[x+1])
    sleep(5)
    


def flow3_Ping(clientName, ClientAddr, Key):
    fThreeSoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    fThreeSoc.connect((ClientAddr, NetPort))
    
    # Generate message 
    mssg = json.dumps({"PING":1,"ClientName": clientName, "HostIP":socket.gethostbyname(socket.gethostname()),"Current-Time":int(round(datetime.now().timestamp()))}).encode("utf8")

    # Print out PING status
    print(f"PING > {clientName}")

    # Send message to the Client, requesting all online accounts 
    fThreeSoc.send(mssg)

    responce = json.loads(fThreeSoc.recv(1024))
    # Testing!
    responce = ({"PING":0, "ClientName":"Test", "Current-Time":int(round(datetime.now().timestamp()))})

    # Need to check the encrypted authenticity


    # If we receve a PONG response and it is within a reasonable timestamp range print!
    if (responce["PING"] == 0 and int(round(datetime.now().timestamp())) - responce['Current-Time'] < 80):
        print( f"PONG < { responce['ClientName'] }")
    
    # Close Connection/Socket
    fThreeSoc.shutdown()
    fThreeSoc.close()

def flow2_Get_Online(hostname, netIP, Key):
    fTwoSoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    fTwoSoc.connect((netIP, NetPort))

    # Send message formatted for requesting online users
    mssg = json.dumps({"Register":0,"ClientName": hostname, "HostIP":socket.gethostbyname(socket.gethostname()),"Current-Time":int(round(datetime.now().timestamp()))}).encode("utf8")
    
    # Send message to the server, requesting all online accounts 
    fTwoSoc.send(mssg)

    # deserialize array, and return contents
    clients= json.loads(fTwoSoc.recv(2048)) 

    # Need to check the encrypted authenticity (before json.loads?)

    # Close Connection/Socket
    fTwoSoc.shutdown()
    fTwoSoc.close()

    # Return list of clients
    return clients


def flow1_Initial_Conn(hostname, netIP):
    # create the socket
    fOneSoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect the socket to the network controller
    fOneSoc.connect((netIP, NetPort))
    
    # Initial message contains everything, later separate them out 
    mssg = json.dumps({"Register": 1, "ClientName": hostname, "HostIP":socket.gethostbyname(socket.gethostname()),"Current-Time":int(round(datetime.now().timestamp()))}).encode("utf8")
    fOneSoc.send(mssg)

    responce = fOneSoc.recv(1024)
    # Parse responce 

    # Close Connection/Socket
    fOneSoc.shutdown()
    fOneSoc.close()

if __name__ == "__main__":
    # Ensure the proper command line arguments are passed 
    # Otherwise exit
    if (len(sys.argv) < 5):
        print("Error! Two arguments are necessary! --network <NET_IP> --name <CLIENT_NAME>")
        exit()

    # This is going to be a lazy way of parsing the arguments...
    # Since there are two valid combinations...
    if (sys.argv[1] == "--network"):
        network = sys.argv[2]
    elif (sys.argv[3] == "--network"):
        network =  sys.argv[4]
    else:
        print("Error in parsing flags! Missing --network flag")
        exit()

    if (sys.argv[1] == "--name"):
        name = sys.argv[2]
    elif (sys.argv[3] == "--name"):
        name = sys.argv[4]
    else:
        print("Error in parsing flags! Missing --name flag")
        exit()

    # Initalize the connection
    flow3_Ping(name, network, 0)



    # Semaphores 
    # https://www.geeksforgeeks.org/synchronization-by-using-semaphore-in-python/