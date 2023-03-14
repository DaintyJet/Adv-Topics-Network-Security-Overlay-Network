from socket import socket, AF_PACKET, AF_INET, SOCK_STREAM, SOCK_RAW, htons, ntohs
from json import dumps, loads


def sniff():
    sock = socket(AF_INET,SOCK_STREAM)
    sock.connect(("127.0.0.1", 9999))
    with open("capture/attacker.txt", "r") as file:
        sock.send(file.read().encode())
    print(f'Response: {sock.recv(512).decode()}')
if __name__ == '__main__':
    sniff()
 