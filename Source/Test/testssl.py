# This is a program for testing SSL sockets in python

# Normal Sockets

# SSL context socket functions

# Json
import json

import socket
import ssl

# Create a default context
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.load_verify_locations(cafile="../Certificate/server_certificate.pem")
#context = ssl.create_default_context()

# Wrap a new socket with the ssl context
conn = context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                           server_hostname="localhost")
# Use the wrapped socket to connect to the server.
conn.connect(("127.0.0.1", 10023))

# Get the peer's (server's) certificate
cert = conn.getpeercert()

# Print the certificate
print(cert)

conn.send("Hello".encode())
#conn.shutdown(socket.SHUT_WR)
msg = conn.read(2048)
print(msg)


