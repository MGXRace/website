import base64
import json
import re
from random import randrange
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, DataError
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

_playerre = re.compile(r'player($|\(\d*\))', flags=re.IGNORECASE)


def get_record(flt):
    """
    Get the maps serialized record race

    Args:
        flt - A kwarg dict to filter race objects by
    
    Returns:
        The serialized race dictionary or None if no race exists
    """
    try:
        record = Race.objects.filter(time__isnull=False, **flt) \
                             .order_by('time')[0]
        return raceSerializer(record)
    except:
        return None


class APIMapList(View):
    """Server API interface for 'randmap' and 'maplist' calls."""

    def get(self, request):
        if not hasattr(request, 'server'):
            raise PermissionDenied

        # load the tags
        try:
            pattern = base64.b64decode(request.GET['pattern'].encode('ascii'), '-_')
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
            limit = 20

        # Filter by the tags we got
        flt = Q(name__regex=pattern) if pattern else Q()
        for t in tags:
            flt = flt & Q(tags__name__iexact=t)

        maps = Map.objects.filter(flt)

        # Randmap call?
        if 'rand' in request.GET:
            count = maps.count()
            if count:
                maps = [maps[randrange(count)]]
            else:
                maps = tuple()
        else:
            maps = maps[start:limit]

        try:
            # Form the response
            data = {
                "start": start,
                "count": len(maps),
                "maps": []
            }

            # Add serialized maps and records
            for map_ in maps:
                smap = mapSerializer(map_)
                smap['record'] = get_record({'map': map_})
                data['maps'].append(smap)

            status = 200

        except DataError:
            data = {"error": "Invalid regular expression"}
            status = 400

        return HttpResponse(json.dumps(data), content_type='application/json', status=status)

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

        # Serialize the data
        data = mapSerializer(map_)
        data['record'] = get_record({'map': map_})

        return HttpResponse(json.dumps(data), content_type='application/json')

    def post(self, request, b64name):
        # Authenticate the request
        if not hasattr(request, 'server'):
            raise PermissionDenied

        mapname = base64.b64decode(b64name.encode('ascii'), '-_')
        try:
            playtime = int(request.POST['playTime'])
            races = int(request.POST['races'])
            tags = json.loads(base64.b64decode(request.POST['tags'].encode('ascii'), '-_'))
        except:
            data = json.dumps({'error': 'Missing parameters'})
            return HttpResponse(data, content_type='application/json', status=400)

        try:
            map_ = Map.objects.get(name=mapname)
        except:
            data = json.dumps({'error': 'Matching map not found'})
            return HttpResponse(data, content_type='application/json', status=404)

        for tagname in tags:
            if tagname.startswith('-'):
                tagname = tagname[1:]
                tag, created = Tag.objects.get_or_create(name=tagname)
                map_.tags.remove(tag)
            else:
                tag, created = Tag.objects.get_or_create(name=tagname)
                map_.tags.add(tag)

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
            player, created = Player.objects.get_or_create(username=username)
            if created:
                if _playerre.match(username):
                    raise Http404

                player.name = username
                player.simplified = username
                player.save()

        except:
            raise Http404

        # Serialize the player
        data = playerSerializer(player)
        data['record'] = get_record({
            'player': player,
            'map_id': request.GET['mid']
        })

        return HttpResponse(json.dumps(data), content_type='application/json')

    def post(self, request, b64name):
        """
        Update player info or create a player
        """
        if not hasattr(request, 'server'):
            raise PermissionDenied

        username = base64.b64decode(b64name.encode('ascii'), '-_')

        # Get the passed parameters
        try:
            mid = int(request.POST['mid'])
            playtime = int(request.POST['playTime'])
            races = int(request.POST['races'])
        except:
            data = json.dumps({'error': 'Missing parameters for user'})
            return HttpResponse(data, content_type='application/json', status=400)

        try:
            player = Player.objects.get(username=username)
            race, created = Race.objects.get_or_create(player=player, map_id=mid)
        except Exception as e:
            print e
            data = json.dumps({'error': 'Could not make race for user/map combination'})
            return HttpResponse(data, content_type='application/json', status=400)

        player.playtime += playtime
        player.races += races
        if created:
            player.maps += 1
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

    def post(self, request, b64name):
        """Update a player's protected nickname."""
        if not hasattr(request, 'server'):
            raise PermissionDenied

        try:
            username = base64.b64decode(b64name.encode('ascii'), '-_')
            player = Player.objects.get(username=username)
        except:
            raise Http404

        try:
            nickname = request.POST['nick']
            if _playerre.match(nickname):
                data = {'error': 'Invalid nickname {}'.format(nickname)}
                status = 400

            else:
                player.name = request.POST['nick']
                player.simplified = stripColorTokens( request.POST['nick'] )
                player.save()
                data = {player.name: True}
                status=200

        except IntegrityError:
            data = {'error': 'Invalid nickname {}'.format(nickname)}
            status = 400

        data = json.dumps(data)
        return HttpResponse(data, content_type='application/json', status=status)


class APIRace(View):
    """Server API interface for Race objects."""

    def get(self, request):
        if not hasattr(request, 'server'):
            raise PermissionDenied

        try:
            mapname = base64.b64decode(request.GET['map'].encode('ascii'), '-_')
            limit = int(request.GET['limit'])
        except:
            data = json.dumps({'error': 'Missing parameters'})
            return HttpResponse(data, content_type='application/json', status=400)

        try:
            map_ = Map.objects.get(name=mapname)
        except:
            data = json.dumps({'error': 'No matching map found'})
            return HttpResponse(data, content_type='application/json', status=400)

        races = Race.objects.filter(map=map_, time__isnull=False).order_by('time')[:limit]
        data = {
            "map": mapname,
            "oneliner": map_.oneliner,
            "count": len(races),
            "races": []
        }

        for race in races:
            srace = raceSerializer(race)
            srace['player'] = playerSerializer(race.player)
            del srace['playerId']
            data['races'].append(srace)

        return HttpResponse(json.dumps(data), content_type='application/json')

    def post(self, request):
        if not hasattr(request, 'server'):
            raise PermissionDenied

        try:
            pid = int(request.POST['pid'])
            mid = int(request.POST['mid'])
            time = int(request.POST['time'])
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
        race, created = Race.objects.get_or_create(player_id=pid, map_id=mid)

        if created:
            player.maps += 1
            player.save()

        # Update race history
        raceh = RaceHistory.objects.create(
            player_id=pid,
            map_id=mid,
            server=request.server,
            time=time,
            playtime=race.playtime,
            created = race.created,
            last_played = race.last_played)

        # Update the record race
        race.server = request.server
        race.time = time
        race.created = timezone.now()
        race.last_played = timezone.now()
        race.save()

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
