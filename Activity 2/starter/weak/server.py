from json import dumps, loads
from os import urandom
from socket import socket, AF_INET, SOCK_STREAM
from _thread import start_new_thread
from xor import XOR


class LoginServer:
    """A simple login server that uses a weak XOR encryption algorithm."""

    def __init__(self, port):
        """
        Args:
            port (int) - the server port
        """

        self.port = port

    def start(self):
        """Listen indefinitely for login requests from multiple clients."""

        sock = socket(AF_INET, SOCK_STREAM)
        sock.bind(('0.0.0.0', self.port))
        sock.listen(10)

        while True:
            (client, _) = sock.accept()

            # start new thread to handle login
            start_new_thread(self.handle_client_login, (client,))

    def handle_client_login(self, client):
        """Handle the client authentication. The protocol works as follows -
            C -> S: Login, N1
            S -> C: N2, K{N1}
            C -> S: K{N2}
            S -> C: Result

        Args:
            client (str) - the client socket

        Returns:
            True if login is successful, False otherwise
        """

        key = open('secrets/key', 'rb').read()
        cipher = XOR(key)

        # Receive Message - C -> S: Login, N1
        received = loads(client.recv(1024))
        nonce1 = bytes.fromhex(received['nonce1'])

        # Send Message - S -> C: N2, K{N1}
        nonce2 = urandom(16)
        enc_nonce1 = cipher.encrypt(nonce1).hex()
        client.send(
            dumps({'nonce2': nonce2.hex(), 'enc_nonce1': enc_nonce1}).encode()
        )

        # Receive Message - C -> S: K{N2}
        received = loads(client.recv(1024))
        enc_nonce2 = received['enc_nonce2']

        if enc_nonce2 == cipher.encrypt(nonce2).hex():
            client.send(b'Login successful')
        else:
            client.close()


if __name__ == '__main__':
    server = LoginServer(port=9998)
    server.start()
