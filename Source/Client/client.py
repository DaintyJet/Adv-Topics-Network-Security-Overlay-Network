# Import library for timestamps 
from datetime import datetime
# Import threading libraries - For semaphores and threading
from threading import *  
# Import sleep from time
from time import sleep
# Import socket for network functionality
import socket
# Import ssl for ssl context stuff
import ssl
# Import the jason library for serializing and deserializing data
import json
# Import sys for command line arguments 
import sys
# Import os for path and file manipulation
import os

# Crypto 
# Import the RSA algorithms
from Crypto.PublicKey import RSA
# Import signing algorithms
from Crypto.Signature import pkcs1_15
# Import Hashing Algorithms 
from Crypto.Hash import SHA256
# Import AES algorithms 
from Crypto.PublicKey import RSA

# Does not work on Matts Machine do ip = <LOCAL>
# sorry for that
# Used to get the IP of the machine (eth0)
#import netifaces as ni
ip = "127.0.0.1" #ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']



### Good practices are in use - see the global variables below
## Ports in use
# The port the server is going to be listening on
NetPort = 9999
# The port the peers of the client (and itself) will be listening on
PeerPort = 9998
# Create a global Semaphore for managing access to the clients list
client_lock = Semaphore(1)
# Create a SSL Client Context to implement SSL on the client sockets
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

# Set the trusted certificate store to the specified file, we will change 
# this to a directory once the system stores individual peer certificates
context.load_verify_locations(cafile="../Certificate/server_certificate.pem")


# Create a global variable for managing the continuation of the program
# If we get an extra run this is not too major so we will try without mutexs
thrdContinue = True




# This is a function that takes a response signed with a private key 
# and will validate it using the public  key passed as an argument
# __________________________________
# Arguments: 
# Response - This is a dictonary in the form "Message":Msg, and "Signature":Signed-Msg
# where Msg is a plaintext string and Signature is the signed message (using pkcs1_15 methods)
#
# key: This is the public key we use to verify it's signature.
# __________________________________
# Return: True if the signature is valid false otherwise  
def client_parse_verify(responce,key):
    
    # Extract the signature which is encoded in a Hex format
    signature = bytes.fromhex(responce["Signature"])

    h = SHA256.new(responce["Message"].encode("utf8"))

    try:
        pkcs1_15.new(key).verify(h, signature)
        return True
    except (ValueError, TypeError):
        return False



# This function is used to manage the client's listening socket 
# and dispatch additional threads to handle new connections (PONG)
# __________________________________
# Arguments: 
# Hostname - This is used to share information with the flow3 pong function
# Key - This is used to share information with the flow3 pong function
# and potentially a key we use to sign messages or setup SSL connections
# __________________________________
# Return: void (none!)
def client_listen(hostname, Key):
    # Create and configure the client's listening socket
    psoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Set a timeout of 5 seconds on the socket
    psoc.settimeout(5)
    # Bind to listen to all addrs on the peer port 
    psoc.bind(("0.0.0.0", PeerPort))
    # Allow 10 concurrent connections (Arbitrary at this point - make it a function or arg later)
    psoc.listen(10)

    # Forever loop - Function is killed when parent thread is
    while 1:
        try: 
            # Accept connection, demux the arguments
            conn, add_port = psoc.accept()
            # Create a thread to respond with a PONG, and start it
            Thread(target=flow3_pong, args=(hostname, conn, add_port, Key,)).start()

        except socket.timeout as ERR:
            # If we timeout, keep looping (This is so non-terminating kills CTL-C are eventually recognized)
            pass



# This function is the "main" function that handles the operations of the client
# This is so the main function can easily be killed leading to the secession of 
# Other operations.
# This will spawn the flow1 thread, flow 2 threads, listener (above) and handel PINGs
# __________________________________
# Arguments: 
# hostname - This is the Client's hostname as defined by a command line argument. 
# This is passed as an argument to the functions/threads this one spawns
#
# netIP - This is the Server's IP (ot domain name) as defined by a command line argument. 
# This is passed as an argument to the functions/threads this one spawns
# 
# Key - This is the Client's Public key or Cert location as determined in Flow1 (To be implemented). 
# This is passed as an argument to the functions/threads this one spawns so SSL sockets can be created.
# __________________________________
# Return: void (none!) 
def client_Driver(hostname, netIP, Key):

    flow1_Initial_Conn(hostname, netIP, Key)
    
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
        for x in range(0,len(clients["Clients"])):
                # May want to do this work on the server's side.
                if not (ip == clients["IPs"][x]):
                    flow3_ping(clients["Clients"][x], clients["IPs"][x], Key)  
        client_lock.release()



# This function handles replying to pings as they are received by the client_listen
# function 
# __________________________________
# Arguments: 
# hostname - This is the Client's hostname as defined by a command line argument. 
# This is passed as an argument to be included in the generated message
#
# netIP - This is the Client's IP (or domain name) as defined by a command line argument. 
# This is passed as an argument to be included in the generated message
# 
# add_port- This is deprecated
# Key - This is redundant
# __________________________________
# Return: void (none!) 
def flow3_pong (hostname, conn, add_port, Key):
            # receive the initial communication from the client  
            recv = json.loads(conn.recv(1024))

            # Extract the Client's name ## ugly implementation
            test = recv["ClientName"]
            # Print to the screen we are PONGing the client
            print(f"PONG > {test}")

            # Generate Pong Message (PING:0 is a pong (Not a pong!))
            mssg = json.dumps({"PING":0,"ClientName": hostname, "HostIP":ip,"Current-Time":int(round(datetime.now().timestamp()))}).encode("utf8")
            
            # send the message
            conn.write(mssg)

# This function handles the Pinging of clients recived in the list 
# from the server in flow 2
# __________________________________
# Arguments:
# clientName: 
# hostname - This is the Peer's hostname that we wish to ping, this is used in the 
# message
#
# ClientAddr - This is the Peer's IP (or domain name) that we wish to ping, this 
# is used in the message, and connection process
# 
# Key - This is the Peers's Public key or Cert location as determined in Flow2 (To be implemented). 
# This is  so SSL sockets can be created.
# __________________________________
# Return:
#  Void (none!)
def flow3_ping(clientName, ClientAddr, Key):
    # Give function access to variables in the Global Scope
    global clients, thrdContinue
    # Create socket to send to individual peers (one socket per peer -- Threads!)
    fThreeSoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Set timeout to prevent hanging 
    fThreeSoc.settimeout(3)
    
    # Error (timeout) handling
    try:
        # Connect to the client
        fThreeSoc.connect((ClientAddr, PeerPort))
        
        # Generate message (PING:1 means this is a ping message
        mssg = json.dumps({"PING":1,"ClientName": clientName, "HostIP":ip,"Current-Time":int(round(datetime.now().timestamp()))}).encode("utf8")

        # Print out PING status
        print(f"PING > {clientName}")

        # Send message to the Client, requesting all online accounts 
        fThreeSoc.write(mssg)

        # Load Response 
        responce = json.loads(fThreeSoc.recv(1024))
       
        # If we receve a PONG response and it is within a reasonable timestamp range print! otherwise ignore
        if (responce["PING"] == 0 and int(round(datetime.now().timestamp())) - responce['Current-Time'] < 10):
            print( f"PONG < { responce['ClientName'] }")
    except socket.error:
        # IF we are unable to connect print this and move on (we have better things!!!)
        print(f"Unable to connect to Client: {clientName} at IP:{ClientAddr}")

    # end connection 
    fThreeSoc.close()


# This function communicates with the server using a SSL wrapped socket. It sends a message requesting 
# The list of clients every 10 seconds, and stores the responce in a globally available variable
# It (to be implemented) will store the certificates of clients in a known trusted location 
# __________________________________
# Arguments:
# hostname - This is the Client's hostname as defined by a command line argument. 
# This is passed as an argument to be included in the generated message
#
# netIP - This is the server's IP (or domain name) as defined by a command line argument. 
# This is used to connect with the server 
#
# Key - deprecated 
# __________________________________
# Return:
#  Void (none!)
def flow2_Get_Online(hostname, netIP, Key):
    # Access Global clients dictionary and SSL server context
    global clients, context, thrdContinue

    # Continue until user input (defined in main)
    while thrdContinue:
        # sleep for 10 seconds 
        sleep(10)

        # Create a ssl wrapped socket for connections to the server
        fTwoSoc = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=netIP)
        # use the ssl socket to connect to the server 
        fTwoSoc.connect((netIP, NetPort))

        # Send message formatted for requesting online users (Flag = 1)
        # This will be encrypted as is it passed through the SSL wrapped socket
        mssg = json.dumps({"Flag":1,"ClientName": hostname, "HostIP":ip,"Current-Time":int(round(datetime.now().timestamp()))}).encode("utf8")
        
        # Send message to the server, requesting all online accounts 
        fTwoSoc.write(mssg)

        # Protect the client arr from race conditions
        client_lock.acquire()

        # recieve all of the responce (End triggered by shutdown RD WR or both
        responce = bytearray()
        while True:
            temp = fTwoSoc.recv(2048)
            if not temp:
                 break
            responce.extend(temp)
        print(responce)
        
        #deserialize array, and return contents
        clients= json.loads(responce) 

        # Release semaphore (Allow Flow 3 to function)
        client_lock.release()

        # Close Connection/Socket
        fTwoSoc.close()


# This function registers the client with the server it is not already registered.
# It (to be implemented) stores the client's signed certificate at a known location 
# so it can be used to implement a SSL server context (with its already existing private key)
# __________________________________
# Arguments:
# hostname - This is the Client's hostname as defined by a command line argument. 
# This is passed as an argument to be included in the generated message
#
# netIP - This is the Server's IP (or domain name) as defined by a command line argument. 
# This is used to connect with the server
#
# public_key - This is the client's public key we wish to use when generating certificates.  
# __________________________________
# Return:
#  Void (none!)
def flow1_Initial_Conn(hostname, netIP, public_key):
    # Allow access to global SSL context object
    global context

    # create the socket and wrap in SSL context
    fOneSoc = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname="localhost")
    # Connect the socket to the network controller
    fOneSoc.connect((netIP, NetPort))

    # Initial registration message (Flag:0 is for registration) this will be encrypted as it is through a SSL context
    mssg = json.dumps({"Flag": 0, "ClientName": hostname, "HostIP":ip, "ClientPubKey":str(public_key),"Current-Time":int(round(datetime.now().timestamp()))}).encode("utf8")
    # Write message to socket (send)
    fOneSoc.write(mssg) 

    # This first message should be whether we are registered or not.
    responce = (json.loads(fOneSoc.recv(2048)))
    
    # If we receive a flag of value 0 we would need to parse the message containing the client certificate (this will need to be verified)
    # Otherwise we have no need to do anything as we do not have a certificate
    if (responce["Flag"] == 1):

        # import the server's public key from a cert
        key = RSA.import_key(open('../Certificate/server_certificate.pem').read())
        
        # Get responce containing server's certificate
        responce = json.loads(fOneSoc.recv(2048))
        # Verify and output a message (write to a file once implemented)
        if not (client_parse_verify(responce,key)):
            print("Error in verifying the certificate")
            return False
        else:
            print("Cert is Good")
   
    # Close Connection/Socket
    fOneSoc.shutdown(socket.SHUT_RD)
    fOneSoc.close()


## main function!
# This function Parses the command line arguments, generates a asymmetric key pair if they
# Do not already exist.
# It spawns to driver function, and waits for user input, once it is received the program should close (hopefully)
# __________________________________
# Arguments: None
# __________________________________
# Return: void (none)
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

    # If the key files do not exist generate them
    if not (os.path.exists("Keys/ClientKeys/")):
        # Make Keys Directory
        os.makedirs(os.path.dirname("Keys/ClientKeys/"), exist_ok=True)

        # Create Public and Private RSA key pair
        key = RSA.generate(2048)
        private_key = key.export_key()
        file_out = open("Keys/ClientKeys/private.pem", "wb")
        file_out.write(private_key)
        file_out.close()

        public_key = key.publickey().export_key()
        file_out = open("Keys/ClientKeys/receiver.pem", "wb")
        file_out.write(public_key)
        file_out.close()



    # Spawn driver function
    drivert = Thread(target = client_Driver, args = (name, network, RSA.import_key(open("Keys/ClientKeys/receiver.pem").read())))
    # Make the driver thread a daemon thread so it is killed once the main is exited 
    drivert.daemon = True
    drivert.start()
    
    # once input is received, set loops to end and kill all spawned functions (by dying)
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