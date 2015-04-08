import hashlib
import base64
from collections import OrderedDict
from django.contrib.auth.hashers import BasePasswordHasher, mask_hash
from django.utils.crypto import constant_time_compare
from django.utils.translation import ugettext_noop as _


class SHA256Hasher(BasePasswordHasher):
    """Repeatedly hashes an unsalted password with sha256"""
    algorithm = "sha256"
    iterations = 100000
    digest = hashlib.sha256

    def salt(self):
        """No salt for us at the moment"""
        return ''

    def verify(self, password, encoded):
        """Verify the password encodes to encoded"""
        encoded_2 = self.encode(password, '')
        return constant_time_compare(encoded, encoded_2)

    def encode(self, password, salt):
        """Encode the password for DB storage"""
        assert salt == ''

        h = self.digest(password.encode('utf-8'))
        encoded = h.digest()
        for i in range(1, self.iterations):
            h = self.digest(encoded)
            encoded = h.digest()
        encoded = base64.b64encode(encoded, b'-_')

        return '{}$${}'.format(self.algorithm, encoded)

    def safe_summary(self, encoded):
        assert encoded.startswith('sha256$$')
        hash_ = encoded[8:]
        return OrderedDict([
            (_('algorithm'), self.algorithm),
            (_('hash'), mask_hash(hash_)),
        ])
