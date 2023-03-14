# This is a Placeholder

# Import library for timestamps 
from datetime import datetime
# Import socket for network functionality
import socket
# Import the jason library for serializing and deserializing data
import json


netsoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
netsoc.bind(("0.0.0.0", 9999))

while 1:
    netsoc.listen(10)
    clientSoc, clientAddr = netsoc.accept()
    # Parse the flow


    # Debug
    mssg = clientSoc.recv(2048).decode("utf8")
    print(mssg)
    clientSoc.send(json.dumps(["Host1", "Host2"]).encode("utf8"))
    