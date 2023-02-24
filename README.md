# Project 

This is a project for the Adv. Topics in Network Security class at the University of Massachusetts Lowell. 

Group: Tirth Kothari, Anirudh Sunil, Matthew Harper

The following is a reiteration of some tasks from the assignment PDF

## Objective 
The goal of this project is to enable students to get hands-on experience creating secure networked architectures. Each team will implement an encrypted overlay network, and implement clients that will use this overlay network to discover and communicate with other clients connected to the network. Creating such a network will give students an intution of how overlay networks work on services such as Kubernetes and Docker Swarm.

## Requirements 
Design and implement an encrypted overlay network that consists of a single network end-point and multiple clients that can connect to this network. Each client can communicate with other clients as long as these clients are on the same network.

## Network Design
The traffic flows as follows -
*  Flow 1 -> This flow occurs every time a new client is started. Each client has a name (e.g.,
client1.c6610.uml.edu, client2.c6610.uml.edu) that it registers with the network.
* Flow 2 -> This flow occurs every 10 seconds on each running client. Each client connects with the
network to retrieve the names of all other clients connected to the network.
* Flow 3 -> This flow occurs every 15 seconds on each running client. Each client establishes a connection
with other clients and sends the message PING to them. Each client responds back with a PONG

## Implementation
The network source code must be in a file called [network.py](Source/Network/network.py). The client source code must be in a file called [client.py](Source/Client/client.py). The programming language of choice is Python 3, which is already instead on your Linux VMs.

___

## Documents 
Planning: Google Doc or [Local Markdown](Documentation/Planning.md)

Threats: Google Doc or [Local Markdown](Documentation/Threats.md)

Security: Google Doc or [Local Markdown](Documentation/Security.md)

Running: [Local Markdown](Source/README.md)