# Import library for timestamps 
from datetime import datetime
# Import threading libraries - For semaphores and threading
from threading import *  
# Import sleep from time
from time import sleep
# Import socket for network functionality
import socket
# Import the jason library for serializing and deserializing data
import json
# Import sys for command line arguments 
import sys
# Used to get the IP of the machine (eth0)
#import netifaces as ni
ip = "127.0.0.1" #ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']


NetPort = 9999
PeerPort = 9998
# Create a global Semaphore for managing access to the clients list
client_lock = Semaphore(1)

# Create a global variable for managing the continuation of the program
# If we get an extra run this is not too major so we will try without mutexs
thrdContinue = True

#


def client_listen(hostname, Key):
    psoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    psoc.settimeout(5)
    psoc.bind(("0.0.0.0", PeerPort))
    psoc.listen(5)
    while 1:
        try: 
            conn, add_port = psoc.accept()
            Thread(target=flow3_pong, args=(hostname, conn, add_port, Key,)).start()

        except socket.timeout as ERR:
            pass

# This is not waiting the appropriate amount of time, this is a known issue, currently for testing
def client_Driver(hostname, netIP, Key):

    global clients, thrdContinue
    flow2t = Thread(target = flow2_Get_Online , args = (hostname, netIP, Key,))
    flow2t.daemon = True
    flow2t.start()
    

    flow3t = Thread(target = client_listen , args = (hostname, Key,))
    flow3t.daemon = True
    flow3t.start()

    while thrdContinue:
        sleep(15)
        client_lock.acquire()
        # dictc = {"ClientName":[], "IP":[], "CERT":[]}
        for x in range(0,len(clients), 2):
                flow3_ping(clients[x], clients[x+1], Key)  
                pass
        client_lock.release()
    
def flow3_pong (hostname, conn, add_port, Key):
            # Decrypt and validate user
            recv = json.loads(conn.recv(1024))

            # Ugly
            test = recv["ClientName"]
            print(f"PONG > {test}")

            mssg = json.dumps({"PING":1,"ClientName": hostname, "HostIP":ip,"Current-Time":int(round(datetime.now().timestamp()))}).encode("utf8")
            conn.send(mssg)


def flow3_ping(clientName, ClientAddr, Key):
    global clients, thrdContinue

    fThreeSoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    fThreeSoc.connect((ClientAddr, PeerPort))
    
    # Generate message 
    mssg = json.dumps({"PING":1,"ClientName": clientName, "HostIP":ip,"Current-Time":int(round(datetime.now().timestamp()))}).encode("utf8")

    # Print out PING status
    print(f"PING > {clientName}")

    # Send message to the Client, requesting all online accounts 
    fThreeSoc.send(mssg)

    responce = json.loads(fThreeSoc.recv(1024))
    # Testing!
    responce = ({"PING":0, "ClientName":"Test", "Current-Time":int(round(datetime.now().timestamp()))})

    # Need to check the encrypted authenticity


    # If we receve a PONG response and it is within a reasonable timestamp range print!
    if (responce["PING"] == 0 and int(round(datetime.now().timestamp())) - responce['Current-Time'] < 10):
        print( f"PONG < { responce['ClientName'] }")
    
    # Close Connection/Socket
    #fThreeSoc.shutdown()
    fThreeSoc.close()

def flow2_Get_Online(hostname, netIP, Key):
    global clients
    while thrdContinue:
        sleep(10)

        fTwoSoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        fTwoSoc.connect((netIP, NetPort))

        # Send message formatted for requesting online users
        mssg = json.dumps({"Flag":1,"ClientName": hostname, "HostIP":ip,"Current-Time":int(round(datetime.now().timestamp()))}).encode("utf8")
        
        # Send message to the server, requesting all online accounts 
        fTwoSoc.send(mssg)

        # Protect the client arr
        client_lock.acquire()
        # deserialize array, and return contents
        clients= json.loads(fTwoSoc.recv(2048)) 

        # Need to check the encrypted authenticity (before json.loads?)
        client_lock.release()

        # Close Connection/Socket
        #fTwoSoc.shutdown()
        fTwoSoc.close()
        # Return list of clients
    #return clients


def flow1_Initial_Conn(hostname, netIP):
    # create the socket
    fOneSoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect the socket to the network controller
    fOneSoc.connect((netIP, NetPort))
    
    # Initial message contains everything, later separate them out 
    mssg = json.dumps({"Flag": 0, "ClientName": hostname, "HostIP":ip,"Current-Time":int(round(datetime.now().timestamp()))}).encode("utf8")
    fOneSoc.send(mssg)

    responce = fOneSoc.recv(1024)
    # Parse responce
     
    print(responce.decode())
    # Close Connection/Socket
    #fOneSoc.shutdown()
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
    drivert = Thread(target = client_Driver, args = (name, network, 0))
    # Make the driver thread a daemon thread so it is killed once the main is exited 
    drivert.daemon = True
    #drivert.start()
    flow1_Initial_Conn(name, network)
    input()
    # Set Continue flag to false
    thrdContinue = False
    # Send a kill message to the local server so it terminates (Exits accept loop)
    
    
    
    #esoc = socket.socket((socket.AF_INET, socket.SOCK_STREAM))
    #esoc.connect(("127.0.0.1", 9999))
    #msg = json.dumps({"PING":-1, "ClientName": "localhost", "HostIP":socket.gethostbyname(socket.gethostname()),"Current-Time":int(round(datetime.now().timestamp()))})
    
    
    
    
#Drivers 
# Semaphores 
# https://www.geeksforgeeks.org/synchronization-by-using-semaphore-in-python/