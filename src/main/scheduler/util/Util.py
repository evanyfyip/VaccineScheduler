import hashlib
import os


class Util:
    def generate_salt():
        """
        Returns a string of random bytes

        Returns
        -------
        utf-8 encoded string
            Random string used for salt
        """
        return os.urandom(16)

    def generate_hash(password, salt):
        """
        Generates the hashed key for the given
        password and salt.

        Parameters
        ----------
        password : str
            User inputed string for password
        salt : Utf-8 encoded string
            Random Utf-8 byte like string object
            used to randomize the password.

        Returns
        -------
        [type]
            [description]
        """
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'), # encode as bytes like object
            salt,
            100000,
            dklen=16 # derived key length
        )
        return key
