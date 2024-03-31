"""
bs64encode(3位随机数 + md5(time()) + '!/&/%/#' + '/' + id + '/' + choices(chars, k=10))
"""
from time import time
from hashlib import md5
from re import match
from random import randint, choices, choice
import base64


class Encryption:
    def __init__(self):
        self.chars = 'abcdefghijklmnopqrstuvwxyz'
        self.sign = '!&%#'
        self.md5 = md5()
        self.logo = '/'

    @property
    def _random_num(self):
        return randint(100, 999)

    @property
    def _random_chars(self):
        return ''.join(choices(self.chars, k=10))

    @property
    def _timestamp(self):
        self.md5.update(str(time()).encode())
        return self.md5.hexdigest()

    @property
    def _sign(self):
        return choice(self.sign)

    def _encode(self, _id, _time):
        _random_num = self._random_num
        _timestamp = self._timestamp
        _sign = self._sign
        _random_chars = self._random_chars
        info = 'id=%s&time=%s' % (_id, _time)
        b64_info = base64.b64encode(info.encode()).decode()
        string = f'{_random_num}{_timestamp}{_sign}{self.logo}{b64_info}{self.logo}{_random_chars}'.encode()
        return base64.b64encode(string).decode()

    def encode(self, _id, _time):
        """对id进行编码"""
        return self._encode(_id, _time)

    def decode(self, token):
        """解码id"""
        token = base64.b64decode(token).decode()
        b64_info = match(f'.*(!|&|%|#|){self.logo}(.*?){self.logo}.*', token).groups()[1]
        info = base64.b64decode(b64_info).decode()
        return match('id=(\\d+)&time=(\\d+)', info).groups()


def decryption(secret):
    encryption = Encryption()
    return encryption.decode(secret)


# if __name__ == '__main__':
#     encryption = Encryption()
#     encrypt = encryption.encode(30, 20)
#     decrypt = encryption.decode(encrypt)
#     print(encrypt)
#     print(decrypt)
