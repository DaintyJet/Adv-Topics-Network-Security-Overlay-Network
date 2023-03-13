from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from json import dumps, loads
from requests import post as post_request
from socket import socket, AF_INET, SOCK_STREAM
from _thread import start_new_thread


class LoginServer:
    """A simple login server that is vulnerable to a replay attack."""

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
            C -> S: Login, K{U, P}
            S -> C: Result

        Args:
            client (str) - the client socket

        Returns:
            True if login is successful, False otherwise
        """

        key = open('secrets/key', 'rb').read()
        cipher = AES.new(key, AES.MODE_ECB)

        # Received Message - C -> S: Login, K{U, P}
        received = loads(client.recv(1024))
        message = bytes.fromhex(received['message'])
        credentials = loads(unpad(cipher.decrypt(message), 16))

        # internally, send the credentials to another server
        server = 'http://192.168.0.172:8888/login'
        data = dumps({'username': credentials['username'],
                      'password': credentials['password']})

        response = post_request(server, data=data)
        if response.status_code == 200:
            client.send(b'Login successful')
        else:
            client.close()


if __name__ == '__main__':
    server = LoginServer(port=9999)
    server.start()
