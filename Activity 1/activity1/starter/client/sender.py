from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from json import dumps, loads
from requests import post as post_request
from socket import socket, AF_INET, SOCK_STREAM


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
        if response.status_code != 200:
            raise Exception('Unexpected response code from the server.')

        return loads(response.content)['token']

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

        response = post_request(server, data=data)
        if response.status_code != 200:
            raise Exception('Unexpected response code from the server.')

        return loads(response.content)

    def send_message(self, receiver, message):
        """Send a confidential message to the receiver.

        Args:
            receiver (str) - the receiver username
            message (str) - the confidential message
        """
        recever_info = self.get_receiver_info(receiver)
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((recever_info["ip_addr"], 9092))

        
        AES_OBJ = AES.new(str.encode(recever_info["secret"]), AES.MODE_ECB)
        enc_messg = (AES_OBJ.encrypt(pad(message.encode(), 16))).hex()
        data = (dumps({"enc_messg":enc_messg, "enc_recever_info":recever_info["senderinfo"]})).encode()

        sock.send(data)

        return 1


if __name__ == '__main__':
    # Update username with your email address (all lowercase)
    # Update receiver with receiver email address (all lowercase)
    sender = Sender(server='http://192.168.0.172:8888',
                    username='matthew_harper@student.uml.edu',
                    password='1qazxsW@1')
    sender.send_message(receiver='matthew_harper@student.uml.edu', message='Hello')
    # tirthkamlesh_kothari@student.uml.edu
