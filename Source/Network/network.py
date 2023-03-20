# This is a Placeholder

# Import library for timestamps 
from datetime import datetime
# Import socket for network functionality
import socket
# Import the jason library for serializing and deserializing data
import json

from threading import *

netsoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
netsoc.bind(("0.0.0.0", 9999))


def test(clientSoc):
    # Debug
    print("Here")
    mssg = clientSoc.recv(2048).decode("utf8")
    print(mssg)
    clientSoc.send(json.dumps(["TEST", "127.0.0.1"]).encode("utf8"))
    clientSoc.close()

while 1:
    netsoc.listen(10)
    clientSoc, clientAddr = netsoc.accept()
    Thread(target=test,args=(clientSoc,)).start()
    # Parse the flow
