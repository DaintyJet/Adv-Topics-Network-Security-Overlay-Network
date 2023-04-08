# Import Date time for Timestamps
from datetime import datetime
# Import Hashing function for certificates
from Crypto.Hash import SHA256
# Import AES and RSA Ciphers
from Crypto.Cipher import AES, PKCS1_OAEP
# For Signatures
from Crypto.Signature import pkcs1_15
# Import RSA PK Functions
from Crypto.PublicKey import RSA
# Import socket from socket functions
import socket
# import ssl functions for network <-> client communications
import ssl

# Import threading to support multithreaded 
import threading

# Import Json for json functions!
import json
# Import OS functionality
import os

# Used to get the IP of the machine (eth0)
import netifaces as ni
ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr'] # = "127.0.0.1" #

# Server Class
class Server:

    # This is the initializer 
    # __________________________________
    # Arguments:
    # self - Its a class function
    # port - the port to listen on
    # __________________________________
    # Return: 
    # void (none)
    def __init__(self, port):
        self.port = port
        self.clients = { "Hostname":[],"HostIP":[], "Cert":[]} #storing the clients
        self.list_lock = threading.Semaphore(1)
    
    # This function start the server, configuring the socket, SSL context
    # And dispatches threads to handel new connections
    # It will load the list of existing clients if they already exist
    # __________________________________
    # Arguments:
    # Self - CLASS
    # __________________________________
    # Return: 
    # void (none!)
    def start(self):
        #Here the server checks if the client-lists exists
        #loads the clients which already exists
        if (os.path.exists("client-list.json")):
            with open("client-list.json") as FILE:
               self.clients = json.load(FILE) 
        
        # Create server listening socket 
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Set basic timeout 
        self.sock.settimeout(3)
        # Listen to all on specified port
        self.sock.bind(("0.0.0.0", self.port))
        # listen for 10 connections 
        self.sock.listen(10)


        # Create the SSL socket
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        # Load server's cert and key
        context.load_cert_chain(certfile="../Certificate/server_certificate.pem", keyfile="../Certificate/server_key.key")
        

        # Make notice that server is listening
        print(f'Server listening on port {self.port}')

        # Infinite loop for handling connections
        while True:
            try:
                # Accept connection 
                conn, addr = self.sock.accept()
                # Wrap connection in SSL context
                wrapped_conn = context.wrap_socket(conn, server_side=True)
                # Make notice of new client on port X
                print(f'New client connected: {addr}')
                # Create and start thread for handling the client 
                threading.Thread(target=self.handle_client, args=(wrapped_conn,addr)).start()
            except socket.timeout as ERR:
                pass

    
    
    # This function handles the client connection. It will respond with the
    # necessary information and a flag determining the information contained as described below
    #   Flag = -1 is a failure is a rejection of connections 
    #   Flag = 0 is a successful registration
    #   Flag = 1 is a non-updating registration
    #   Flag = 2 is a successful query, additional fields expected
    # __________________________________
    # Arguments: 
    # conn - The wrapped ssl socket used to handel connections
    # addr - addr of client ascertained by the socket
    # __________________________________
    # Return:
    # void (none) 
    def handle_client(self, conn, addr):

        # Receive Client's request 
        clientmsg = conn.recv(2048)
        # load it.
        msg = json.loads(clientmsg)

        # Parse the request type
        # If the flag is 1, the client is requesting a list of all connected clients, we check if the send (msg encoded) is the same as the socket addr
        # and that the timestamp is valid (Long duration in out case for testing)
        if ( msg["Flag"] == 1 and msg["HostIP"] == addr[0] and (msg["Current-Time"] - int(round(datetime.now().timestamp())) < 10 )):
            
            # Grab Semaphore
            self.list_lock.acquire()

            # Parse the msg - is the client not registerd
            if ( msg["ClientName"] not in self.clients["Hostname"] and msg["HostIP"] not in self.clients["HostIP"]):
                # If the client is not registered we should not be providing information
                conn.write(json.dumps({"Flag":-1, "NetworkIP":ip, "Current-Time":int(round(datetime.now().timestamp()))}).encode("utf8"))
                # Nothing else is needed, return.
                return
            
            # Generate response (Successful update (FLAG = 2)
            response = {"Flag":2, "NetworkIP":ip, "Clients": self.clients["Hostname"], "IPs":self.clients["HostIP"], "Certs":self.clients["Cert"], "Current-Time":int(round(datetime.now().timestamp()))}

            # Send reply SSL context means this is encrypted
            conn.write(json.dumps(response).encode("utf8"))

            # Release the lock - so other operations on the client list can occur
            self.list_lock.release()

        # IF the flag is 0 the client is registering, same precautions as above are taken    
        elif ( msg["Flag"] == 0 and msg["HostIP"] == addr[0] and (msg["Current-Time"] - int(round(datetime.now().timestamp())) < 10 )):
            
            # acquire Semaphore 
            self.list_lock.acquire()
            # Generate generic initial response (Failure is 0)
            response = {"Flag":0, "NetworkIP":ip, "Current-Time":int(round(datetime.now().timestamp()))}
            

            # This is going to parse the registering message
                # is it already registered
            if ( msg["ClientName"] not in self.clients["Hostname"] and msg["HostIP"] not in self.clients["HostIP"]):
                # Registering the client

                # Inform the client the status of the transaction (Success - they are not registered)
                response["Flag"] = 1
                conn.write(json.dumps(response).encode())
                
                # Create a certificate -- Placeholder!
                cert = json.dumps({"ClientName":msg["ClientName"], "ClientIP":msg["HostIP"] ,"ClientPubKey":str(msg["ClientPubKey"])})

                # Extract server's private key 
                key = RSA.import_key(open('../Certificate/server_key.key').read())
                # create a hash object with the handmade cert
                h = SHA256.new(cert.encode("utf8"))
                # sign it
                signature = (pkcs1_15.new(key).sign(h)).hex()
                
                # Create a message to send the cert
                response = json.dumps({"Message":cert, "Signature": signature})

                # send the cert
                conn.write(response.encode("utf8"))

                # We store the necessary info
                self.clients["Hostname"].append(msg["ClientName"])
                self.clients["HostIP"].append(msg["HostIP"])
                self.clients["Cert"].append(response)
                
                # Write Dictionary to the file 
                with open("client-list.json", "w") as FILE:
                    FILE.write(json.dumps(self.clients))
                
            else:
                # Respond to the client - saying they are already registered
                conn.write(json.dumps(response).encode("utf8"))
            self.list_lock.release()
        
        # close connection
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()
    # Function to generate the client's certificate
    #def create_client_cert(client_public_key):
        # To be implemented 
    #   pass
        
# Main function to initialize and start a server object      
# __________________________________
# Arguments:
# none
# __________________________________
# Return:
# void (none)      
if __name__ == '__main__':
    # Init server to listen on 9999
    server = Server(9999)
    # Start server
    server.start()
    # on input stop! (kill by killing parent thread!)
    input()
