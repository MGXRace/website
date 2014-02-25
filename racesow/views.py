import base64
import json
from django.http import HttpResponse, Http404
from .models import (
    Tag,
    Map,
    Server,
    Race,
    Checkpoint,
    Player)
from .serializers import (
    mapSerializer,
    playerSerializer,
    raceSerializer)
from .utils import authenticate


class APIMap(View):
    """Server API insterafce for Map objects."""

    def get(self, request, b64name):
        """Returns the map id and best race record if it exists"""
        # Authenticate the request
        if not hasattr(request, 'server'):
            raise PermissionDenied

        mapname = base64.b64decode(b64name.encode('ascii'), '-_')
        map_, created = Map.objects.get_or_create(name=mapname)

        # Load the best race
        try:
            record = Race.objects.filter(map=map_.id).order_by('time')[0]
            record = raceSerializer(record)
        except:
            record = None

        # Serialize the data
        data = mapSerializer(map_)
        data['record'] = raceSerializer(record_) if record else None

        return HttpResponse(json.dumps(data), content_type='application/json')


class APIPlayer(View):
    """Server API interface for Player objects."""

    def get(self, request, b64name):
        """
        Returns player data.
        """
        # Authenticate the request
        if not hasattr(request, 'server'):
            raise PermissionDenied

        # Authenticate client signature
        try:
            username = base64.b64decode(b64name.encode('ascii'), '-_')
            player = Player.objects.get(user__username=username)
            algo, salt, hash_ = player.user.password.split('$', 3)
            assert authenticate(request.GET['uTime'], hash_, request.GET['cToken'])
        except:
            raise Http404

        # Serialize the player
        data = playerSerializer(player)

        # Attach record run if requested
        try:
            race = Race.objects.get(player=player, map_id=request.GET['mid'])
            data['record'] = raceSerializer(race)
        except:
            data['record'] = None

        return HttpResponse(json.dumps(data), content_type='application/json')


class APINick(View):
    """Check if a nickname is protected."""

    def get(self, request, b64name):
        """Check if a player with the nickname exists."""
        if not hasattr(request, 'server'):
            raise permissionDenied

        nick = base64.b64decode(b64name.encode('ascii'), '-_')
        player = Player.objects.filter(name__iexact=nick)
        data = json.dumps({nick: player.exists()})
        return HttpResponse(data, content_type='application/json')


class APIRace(View):
    """Server API interface for Race objects."""

    def get(self, request):
        if not hasattr(request, 'server'):
            raise permissionDenied

        #TODO
        return HttpResponse('Feature not implemented yet!', content_type='text/plain', status=501)