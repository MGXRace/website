import base64
import hashlib

def authenticate(uTime, key, token):
    """Returns true if the token was generated from uTime and key"""
    h = hashlib.sha256("{}|{}".format(uTime, key))
    return base64.b64encode(h.digest(), '-_') == token.replace(' ', '+')

def stripColorTokens(msg):
    result = ""
    i = 0
    while i < len(msg):
        if msg[i] == "^" and i+1 < len(msg):
            if msg[i+1].isdigit():
                i += 2
                continue
            elif msg[i+1] == "^":
                i += 1

        result += msg[i]
        i += 1
    return result