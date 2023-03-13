from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad,pad
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
        while(1)
            sock = socket(AF_INET, SOCK_STREAM)
            sock.bind(('0.0.0.0', 9092))
            sock.listen(10)
            (client_sock, client_addr) = sock.accept()

            test = client_sock.recv(1024)
            responce = loads(test.decode())
            #print(responce["enc_recever_info"])
            self.handle_user_message(responce)
            pass

    def handle_user_message(self, received):
        """Parse the received encrypted message, decrypt and print the
        confidential message.

        Args:
            received (str) - the received encrypted message
        """
        #AES Create
        AES_OBJ = AES.new(str.encode(self.token), AES.MODE_ECB)
        #ct = AES_OBJ.encrypt(pad(b"Matt",16))
        decrypt_info = unpad(AES_OBJ.decrypt(bytes.fromhex(received["enc_recever_info"])),16)
        decrypt_info = loads(decrypt_info)
        
        AES_OBJ = AES.new(str.encode(decrypt_info["secret"]), AES.MODE_ECB)
        decrypt_mssg = unpad(AES_OBJ.decrypt(bytes.fromhex(received["enc_messg"])),16)
        print(decrypt_mssg)
        #AES Decrypt and verify (GCM)
        # TODO
        pass


if __name__ == '__main__':
    # Update username with your email address (all lowercase)
    receiver = Receiver(server='http://192.168.0.172:8888',
                        username='matthew_harper@student.uml.edu',
                        password='1qazxsW@1')
    receiver.receive_messages()
