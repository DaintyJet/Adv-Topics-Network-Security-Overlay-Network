from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from json import dumps, loads
from requests import post as post_request
from socket import socket, AF_INET, SOCK_STREAM


class Receiver:
    def __init__(self, server, username, password):
        """
        Args:
            server (str) - the server url
            username (str) - the login username
            password (str) - the login password
        """

        self.server = server
        self.username = username
        self.token = self.get_login_token(password)

    def get_login_token(self, password):
        """Connect with the server, provide correct username and password, and
        obtain the login token.

        Args:
            password (str) - the login password

        Returns:
            A login token for future operations
        """

        server = self.server + '/login'
        data = dumps({'username': self.username, 'password': password})

        response = post_request(server, data=data)
        if response.status_code != 200:
            raise Exception('Unexpected response code from the server.')

        return loads(response.content)['token']

    def receive_messages(self):
        """Listen indefinitely and receive messages from multiple users."""

        sock = socket(AF_INET, SOCK_STREAM)
        sock.bind(('0.0.0.0', 9999))
        sock.listen(10)
        print(f'Receiver started for user {self.username}.')

        while True:
            (client_sock, _) = sock.accept()
            received = loads(client_sock.recv(2048).decode())

            # the msgtype is a field in the recieved message that will have a
            # value of chat when a user sends a chat message.
            if 'msgtype' in received and received['msgtype'] == 'chat':
                self.handle_user_message(received)
                client_sock.send(b'Received')

            client_sock.close()

    def handle_user_message(self, received):
        """Parse the received encrypted message, decrypt and print the
        confidential message.

        Args:
            received (str) - the received encrypted message
        """

        # all the messages are in hex format, need to convert to bytes.
        sender_info = bytes.fromhex(received['senderinfo'])
        message = bytes.fromhex(received['message'])

        # decrypt the sender info to obtain sender name, ip and secret.
        cipher = AES.new(str.encode(self.token), AES.MODE_ECB)
        sender_info = loads(unpad(cipher.decrypt(sender_info), 16))

        username = sender_info['username']
        ip_addr = sender_info['ip_addr']
        secret_key = sender_info['secret']

        # now, decrypt the encrypted user message using the secret.
        cipher = AES.new(str.encode(secret_key), AES.MODE_ECB)
        message = unpad(cipher.decrypt(message), 16).decode()

        print(f'{username} ({ip_addr}) - {message}')


if __name__ == '__main__':
    # Update username with your email address (all lowercase)
    receiver = Receiver(server='http://192.168.0.172:8888',
                        username='<your email address>',
                        password='1qazxsW@1')
    receiver.receive_messages()
