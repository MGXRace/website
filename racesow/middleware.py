import base64
import hashlib
from .models import Server
from django.core.exceptions import PermissionDenied


def authenticate(uTime, key, token):
    """Returns true if the token was generated from uTime and key"""
    h = hashlib.sha256("{}|{}".format(uTime, key))
    return base64.b64encode(h.digest(), '-_') == token


class ServerAuthenticationMiddleware(object):
    """
    Authenticates a server from querystring parameters 'uTime' and 'sToken'

    If authentication is successful, a `request.server` will be set to the
    `Server` model object that authenticated
    """

    def process_request(self, request):
        # Check for the query parameters
        try:
            uTime = request.GET['uTime']
            sid, token = request.GET['sToken'].split('.')
        except:
            return

        # Validate the token
        try:
            server = Server.objects.get(id=sid)
            assert authenticate(uTime, server.auth_key, token)
        except:
            raise PermissionDenied

        # Attach server to the request
        request.server = server
        

    def process_response(self, request, response):
        pass