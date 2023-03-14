from json import dumps, loads
from os import urandom
from socket import socket, AF_INET, SOCK_STREAM
from xor import XOR


class LoginAttack:
    def __init__(self, server, port):
        """
        Args:
            server (str) - the server address
            port (int) - the server port
        """

        self.server = server
        self.port = port

    def attack(self):
        """Authenticate to a vulnerable server by breaking XOR encryption."""

        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((self.server, self.port))

        # Send Message - C -> S: Login, N1
        nonce1 = urandom(16)
        sock.send(dumps({'type': 'login', 'nonce1': nonce1.hex()}).encode())

        # Receive Message - S -> C: N2, K{N1}
        received = loads(sock.recv(1024))
        nonce2 = bytes.fromhex(received['nonce2'])
        enc_nonce1 = bytes.fromhex(received['enc_nonce1'])

        # break XOR encryption and compute key
        key = self.compute_key(nonce1, enc_nonce1)

        # Send Message - C -> S: K{N2}
        enc_nonce2 = XOR(key).encrypt(nonce2).hex()
        sock.send(dumps({'enc_nonce2': enc_nonce2}).encode())

        print(f'Secret Key: {key}')
        print(f'Response: {sock.recv(512).decode()}')

    def compute_key(self, plaintext, ciphertext):
        """Given a plaintext and ciphertext combination, compute the key that
        was used for encryption.

        Args:
            plaintext (bytes) - the plaintext
            ciphertext (bytes) - the ciphertext

        Returns:
            The computed key used for encryption
        """

        key = []

        for i in range(len(plaintext)):
            key.append(plaintext[i] ^ ciphertext[i])

        return bytes(key)


if __name__ == '__main__':
    attack = LoginAttack(server='localhost', port=9999)
    attack.attack()
