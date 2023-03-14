from json import dumps, loads
from os import urandom
from socket import socket, AF_INET, SOCK_STREAM

class AttackClient:
    def __init__(self, server, port):
        """
        Args:
            server (str) - the server address
            port (int) - the server port
        """

        self.server = server
        self.port = port

    def login(self):
        """Authenticate to the server. The protocol works as follows -
            C -> S: Login, N1
            S -> C: N2, K{N1}
            C -> S: K{N2}
            S -> C: Result
        """

        #key = open('secrets/key', 'rb').read()
        #cipher = AES.new(key, AES.MODE_ECB)

        sock1 = socket(AF_INET, SOCK_STREAM)
        sock1.connect((self.server, self.port))
        
        sock2 = socket(AF_INET, SOCK_STREAM)
        sock2.connect((self.server, self.port))

        # Send Message - C -> S: Login, N1
        nonce1 = urandom(16)
        sock1.send(dumps({'type': 'login', 'nonce1': nonce1.hex()}).encode())

        # Receive Message - S -> C: N2, K{N1}
        received = loads(sock1.recv(1024))
        nonce2 = bytes.fromhex(received['nonce2'])
        
        sock2.send(dumps({'type': 'login', 'nonce1': nonce2.hex()}).encode())

        received = loads(sock2.recv(1024))
        enc_nonce2 = bytes.fromhex(received['enc_nonce1'])
        #enc_nonce1 = received['enc_nonce1']
        #assert enc_nonce1 == cipher.encrypt(nonce1).hex()

        # Send Message - C -> S: K{N2}
        #enc_nonce2 = cipher.encrypt(nonce2).hex()
        sock1.send(dumps({'enc_nonce2': enc_nonce2.hex()}).encode())

        print(f'Response: {sock1.recv(512).decode()}')


if __name__ == '__main__':
    client = AttackClient(server='localhost', port=9999)
    client.login()