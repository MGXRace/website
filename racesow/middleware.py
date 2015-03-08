from django.utils import timezone
import pytz
from .models import Server
from .utils import authenticate
from django.core.exceptions import PermissionDenied


class ServerAuthenticationMiddleware(object):
    """
    Authenticates a server from querystring parameters 'uTime' and 'sToken'

    If authentication is successful, a `request.server` will be set to the
    `Server` model object that authenticated
    """

    def process_request(self, request):
        # Check for the query parameters
        try:
            if request.method == 'GET':
                uTime = request.GET['uTime']
                sid, token = request.GET['sToken'].split('.')
            else:
                uTime = request.POST['uTime']
                sid, token = request.POST['sToken'].split('.')
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
        return response


class TimezoneMiddleware(object):
    def process_request(self, request):
        tzname = request.session.get('django_timezone')
        if tzname:
            try:
                timezone.activate(pytz.timezone(tzname))
            except:
                timezone.deactivate()
        else:
            timezone.deactivate()