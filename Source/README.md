# Programs

This directory contains the "source" files for the network and client programs. This will also contain a description of how to run the programs and the expected output.
## Client
The Client program is located in the [client.py program](Client/client.py) 
This can be run using the following command (assuming we are in the local directory)
```sh
$ python3 client.py --network <NetworkIP> --name <Hostname>
```
The client will register to the serer if it has not already done so. This means ...


## Network
The network controller program is located in the [network.py program](Network/network.py)


### Generating Cert
```sh
$ openssl req  -nodes -new -x509  -keyout server.key -out server.cert
```