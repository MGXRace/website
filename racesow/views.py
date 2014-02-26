import base64
import json
from random import randrange
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.views.generic import View
from django.utils import timezone
from .models import (
    Tag,
    Map,
    Server,
    Race,
    RaceHistory,
    Checkpoint,
    Player)
from .serializers import (
    mapSerializer,
    playerSerializer,
    raceSerializer)
from .utils import authenticate, stripColorTokens


class APIMapList(View):
    """Server API interface for 'randmap' and 'maplist' calls."""

    def get(self, request):
        if not hasattr(request, 'server'):
            raise PermissionDenied

        # load the tags
        try:
            tags = json.loads(base64.b64decode(request.GET['tags'].encode('ascii'), '-_'))
        except:
            data = json.dumps({'error': 'Missing parameters'})
            return HttpResponse(data, content_type='application/json', status=400)

        # load the pagination markers
        try:
            start = int(request.GET['start'])
            limit = start + int(request.GET['limit'])
        except:
            start = 0
            limit = 5

        # Filter by the tags we got
        flt = Q()
        for t in tags:
            flt = flt & Q(tags__name__iexact=t)

        maps = Map.objects.filter(flt)

        # Randmap call?
        if 'rand' in request.GET:
            count = maps.count()
            maps = [maps[randrange(count)]]
        else:
            maps = maps[start:limit]

        # Form the response
        data = {
            "count": len(maps),
            "maps": [mapSerializer(map_) for map_ in maps]
        }
        return HttpResponse(json.dumps(data), content_type='application/json')

    def post(self, request):
        """Add tags to maps here!"""
        raise Http404


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
            record = Race.objects.filter(map=map_).order_by('time')[0]
            record = raceSerializer(record)
        except:
            record = None

        # Serialize the data
        data = mapSerializer(map_)
        data['record'] = record

        return HttpResponse(json.dumps(data), content_type='application/json')

    def post(self, request, b64name):
        # Authenticate the request
        if not hasattr(request, 'server'):
            raise PermissionDenied

        mapname = base64.b64decode(b64name.encode('ascii'), '-_')
        try:
            playtime = int(request.POST['playTime'])
            races = int(request.POST['races'])
        except:
            data = json.dumps({'error': 'Missing parameters'})
            return HttpResponse(data, content_type='application/json', status=400)

        try:
            map_ = Map.objects.get(name=mapname)
        except:
            data = json.dumps({'error': 'Matching map not found'})
            return HttpResponse(data, content_type='application/json', status=404)

        map_.races += races
        map_.playtime += playtime
        map_.save()
        return HttpResponse('', content_type='text/plain')


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
            player = Player.objects.get(user__username__iexact=username)
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

    def post(self, request, b64name):
        """
        Update player info or create a player
        """
        if not hasattr(request, 'server'):
            raise PermissionDenied

        username = base64.b64decode(b64name.encode('ascii'), '-_')
        # cToken means we are registering a player
        if 'cToken' in request.POST:
            return self.create_player(request, username)

        # Get the passed parameters
        try:
            mid = request.POST['mid'].encode('ascii')
            playtime = int(request.POST['playTime'])
            races = int(request.POST['races'])
        except:
            data = json.dumps({'error': 'Missing parameters for user'})
            return HttpResponse(data, content_type='application/json', status=400)

        try:
            player = Player.objects.get(user__username__iexact=username)
            race, created = Race.objects.get_or_create(player=player, map_id=mid)
        except Exception as e:
            print e
            data = json.dumps({'error': 'Could not make race for user/map combination'})
            return HttpResponse(data, content_type='application/json', status=400)

        player.playtime += playtime
        player.races += races
        player.save()

        race.playtime += playtime
        race.last_played = timezone.now()
        race.save()

        raceh = RaceHistory.objects.create(
            player_id=player.id,
            map_id=mid,
            server=race.server,
            time=race.time,
            points=race.points,
            playtime=race.playtime,
            created = race.created,
            last_played = race.last_played)

        return HttpResponse('', content_type='text/plain')

    def create_player(self, request, username):
        """
        Create a user and player
        """
        # Get the passed parameters
        try:
            nick = base64.b64decode(request.POST['nick'].encode('ascii'), '-_')
            pass_ = request.POST['cToken']
            simplified = stripColorTokens(nick)
        except:
            data = json.dumps({'error': 'Missing parameters for user'})
            return HttpResponse(data, content_type='application/json', status=400)

        # Check if the user already exists
        if User.objects.filter(username__iexact=username).exists():
            data = json.dumps({'error': 'User already exists with this name or email'})
            return HttpResponse(data, content_type='application/json', status=400)

        # Check if the player already exists
        if Player.objects.filter(simplified__iexact=simplified).exists():
            data = json.dumps({'error': 'Player already exists with this nickname'})
            return HttpResponse(data, content_type='application/json', status=400)

        # Make the user
        user = User.objects.create_user(username)
        user.password = u'sha256$$' + pass_
        user.save()
        
        # Make the player
        player = Player.objects.create(user=user, name=nick, simplified=simplified)

        # Form the response
        data = playerSerializer(player)
        data['record'] = None
        return HttpResponse(json.dumps(data), content_type='application/json')


class APINick(View):
    """Check if a nickname is protected."""

    def get(self, request, b64name):
        """Check if a player with the nickname exists."""
        if not hasattr(request, 'server'):
            raise PermissionDenied

        nick = base64.b64decode(b64name.encode('ascii'), '-_')
        player = Player.objects.filter(simplified__iexact=nick)
        data = json.dumps({nick: player.exists()})
        return HttpResponse(data, content_type='application/json')


class APIRace(View):
    """Server API interface for Race objects."""

    def get(self, request):
        if not hasattr(request, 'server'):
            raise permissionDenied

        try:
            mapname = base64.b64decode(request.GET['map'].encode('ascii'), '-_')
            limit = int(request.GET['limit'])
        except:
            data = json.dumps({'error': 'Missing parameters'})
            return HttpResponse(data, content_type='application/json', status=400)

        races = Race.objects.filter(map__name=mapname).order_by('time')[:limit]
        data = {
            "map": mapname,
            "count": len(races),
            "races": [raceSerializer(race, cp=False) for race in races]
        }

        return HttpResponse(json.dumps(data), content_type='application/json')

    def post(self, request):
        if not hasattr(request, 'server'):
            raise permissionDenied

        try:
            pid = request.POST['pid']
            mid = request.POST['mid']
            time = request.POST['time']
            checkpoints = json.loads(request.POST['checkpoints'])
        except Exception as e:
            print e
            data = json.dumps({'error': 'Missing parameters for user'})
            return HttpResponse(data, content_type='application/json', status=400)

        try:
            player = Player.objects.get(id=pid)
            map_ = Map.objects.get(id=mid)
        except:
            raise Http404

        # No checks that the race is faster
        # That should be done on the gameserver
        race, created = Race.objects.get_or_create(
            player_id=pid,
            map_id=mid)
        race.server = request.server
        race.time = time
        race.created = timezone.now()
        race.last_played = timezone.now()
        race.save()

        raceh = RaceHistory.objects.create(
            player_id=pid,
            map_id=mid,
            server=request.server,
            time=time,
            points=race.points,
            playtime=race.playtime,
            created = race.created,
            last_played = race.last_played)

        # Delete old checkpoints
        # Since the server will always send all checkpoints, we might can use
        # update_or_create instead of delete/bulk_create
        if not created:
            Checkpoint.objects.filter(race=race).delete()

        # Make new checkpoints
        Checkpoint.objects.bulk_create([
            Checkpoint(race_id=race.id, number=i, time=t) for i, t in enumerate(checkpoints)
        ])

        data = raceSerializer(race)
        return HttpResponse(json.dumps(data), content_type='application/json')