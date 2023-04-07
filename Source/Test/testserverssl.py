# Json
import json

import socket
import ssl

# Function provided by docs
def deal_with_client(conn):
    data = connstream.recv(1024)
    # empty data means the client is finished with us
    
    print(data)
        
       
    # finished with client
    print("Done")
    conn.send("msg".encode())


# Create a server context
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

# Load server's cert and key
context.load_cert_chain(certfile="../Certificate/server_certificate.pem", keyfile="../Certificate/server_key.key")


# Create normal socket so we can accept connections
bindsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
bindsocket.bind(('localhost', 10023))
bindsocket.listen(5)

# Create the SSL socket context on a connection
while True:
    newsocket, fromaddr = bindsocket.accept()
    connstream = context.wrap_socket(newsocket, server_side=True)
    try:
        deal_with_client(connstream)
    finally:
        connstream.shutdown(socket.SHUT_RDWR)
        connstream.close()