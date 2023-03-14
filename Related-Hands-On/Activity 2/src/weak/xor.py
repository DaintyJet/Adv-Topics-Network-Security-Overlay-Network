class XOR:
    """Implementation of a weak encryption algorithm using XOR."""

    def __init__(self, key):
        """
        Args:
            key (bytes) - the secret key
        """

        self.key = key

    def encrypt(self, plaintext):
        """Encrypt the given plaintext using XOR algorithm.

        Args:
            plaintext (bytes) - the plaintext to encrypt

        Returns:
            The encrypted ciphertext
        """

        ciphertext = []

        for i in range(len(plaintext)):
            j = i % len(self.key)

            ciphertext.append(plaintext[i] ^ self.key[j])

        return bytes(ciphertext)

    def decrypt(self, ciphertext):
        """Decrypt the given ciphertext using XOR algorithm.

        Args:
            ciphertext (bytes) - the ciphertext to decrypt

        Returns:
            The decrypted plaintext
        """

        plaintext = []

        for i in range(len(ciphertext)):
            j = i % len(self.key)

            plaintext.append(ciphertext[i] ^ self.key[j])

        return bytes(plaintext)
