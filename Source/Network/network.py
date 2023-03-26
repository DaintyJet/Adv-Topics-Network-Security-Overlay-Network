from datetime import datetime
import socket
import threading
import json
import time
# Used to get the IP of the machine (eth0)
#import netifaces as ni
ip = "127.0.0.1" #ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']

# Server code
class Server:
    def __init__(self, port):
        self.port = port
        self.clients = { "Hostname":[],"HostIP":[] }                                   #storing the clients
        #self.lock = threading.Lock()
        self.list_lock = threading.Semaphore(1)

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(3)
        self.sock.bind(("0.0.0.0", self.port))
        self.sock.listen(5)

        print(f'Server listening on port {self.port}')

        while True:
            try:
                # may want to pass addr as arg
                conn, addr = self.sock.accept()
                print(f'New client connected: {addr}')
                threading.Thread(target=self.handle_client, args=(conn,addr)).start()
            except socket.timeout as ERR:
                pass

    # Flag = -1 is a failure is a rejection of connections 
    # Flag = 0 is a successful registration
    # Flag = 1 is a non-updating registration
    # Flag = 2 is a successful query, additional fields expected
    #   Clients, IPs, <Certs?> 
    def handle_client(self, conn, addr):
        #name = conn.recv(1024).decode()
        # self.clients[name] = conn
        msg = json.loads(conn.recv(2048))
        if ( msg["Flag"] == 1 and msg["HostIP"] == addr[0] and (msg["Current-Time"] - int(round(datetime.now().timestamp())) < 10 )):
            # Grab Semaphore
            self.list_lock.acquire()
            # Parse the msg, TRUE IS PLACEHOLDER
            if ( False and msg["ClientName"] not in self.clients["Hostname"] and msg["HostIP"] not in self.clients["HostIP"]):
                # If the client is not registered we should not be providing information
                conn.send(json.dumps({"Flag":-1, "NetworkIP":ip, "Current-Time":int(round(datetime.now().timestamp()))}).encode("utf8"))
                # Nothing else is needed, return.
                return
            
            # Generate response 
            response = {"Flag":2, "NetworkIP":ip, "Clients": self.clients["Hostname"], "IPs":self.clients["HostIP"], "Current-Time":int(round(datetime.now().timestamp()))}

            # Send response 
            conn.send(json.dumps(response).encode("utf8"))
            
            # Release the lock
            self.list_lock.release()
            print("Good 1")
        elif ( msg["Flag"] == 0 and msg["HostIP"] == addr[0] and (msg["Current-Time"] - int(round(datetime.now().timestamp())) < 10 )):
            # acquire Semaphore 
            self.list_lock.acquire()
            # Success, Already registered, Failure
            response = {"Flag":0, "NetworkIP":ip, "Current-Time":int(round(datetime.now().timestamp()))}
            # This is going to parse the registering message
                # is it already registered
            if ( msg["ClientName"] not in self.clients["Hostname"] and msg["HostIP"] not in self.clients["HostIP"]):
                #Registering the client
                # We store the necessary info
                self.clients["Hostname"].append(msg["ClientName"])
                self.clients["HostIP"].append(msg["HostIP"])

                # Write to file
                pass 
            else:
                response["Flag"] = 1
            # When implementing security we may generate a cert for the client.
            # Respond to the client
            conn.send(json.dumps(response).encode("utf8"))
            self.list_lock.release()
            
        print(msg)

        conn.shutdown(socket.SHUT_RDWR)
        conn.close()
        #while True:
        #    time.sleep(10) # Flow 2
        #    conn.sendall(str(self.clients.keys()).encode())

            
if __name__ == '__main__':
    server = Server(9999)
    server.start()
    input()
