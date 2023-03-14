from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from json import dumps
from socket import socket, AF_INET, SOCK_STREAM


class LoginClient:
    def __init__(self, server, port):
        """
        Args:
            server (str) - the server address
            port (int) - the server port
        """

        self.server = server
        self.port = port

    def login(self, username, password):
        """Authenticate to a vulnerable server using a username and password.

        Args:
            username (str) - the login username
            password (str) - the login password
        """

        plaintext = dumps({'username': username, 'password': password})
        plaintext = pad(plaintext.encode(), 16)

        # encrypt the message using the shared secret
        key = open('secrets/key', 'rb').read()
        message = AES.new(key, AES.MODE_ECB).encrypt(plaintext).hex()

        # expected message is {'type': 'login', 'message': encrypted}
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((self.server, self.port))
        sock.send(dumps({'type': 'login', 'message': message}).encode())
        print(f'Response: {sock.recv(512).decode()}')


if __name__ == '__main__':
    client = LoginClient(server='localhost', port=9999)
    client.login(username='sashank_narain@uml.edu', password='Acadia')
