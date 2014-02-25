import base64
import hashlib

def authenticate(uTime, key, token):
    """Returns true if the token was generated from uTime and key"""
    h = hashlib.sha256("{}|{}".format(uTime, key))
    return base64.b64encode(h.digest(), '-_') == token