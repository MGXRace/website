import base64
import json
from random import randrange

from django.core.exceptions import PermissionDenied
from django.db import DataError, IntegrityError
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.utils import timezone
from django.views.generic import View

from racesow.models import Map, Tag, Player, Race, RaceHistory, Checkpoint
from racesow.serializers import mapSerializer, playerSerializer, raceSerializer
from racesow.services import get_record, is_default_username
from racesow.utils import strip_color_tokens
from racesowold.models import Map as Mapold, PlayerMap
from racesowold.serializers import raceSerializer as raceoldSerializer, playerSerializer as playeroldSerializer


__author__ = 'Mark'


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

        # Filter by enabled maps
        flt = Q(enabled=True)

        # Filter by the name and/or tags
        if pattern:
            flt = flt & Q(name__iregex=pattern)
        for t in tags:
            flt = flt & Q(tags__name__iexact=t)

        maps = Map.objects.filter(flt).order_by('name')

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
    """Server API interface for Map objects."""

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
        try:
            new_oneliner = str(request.POST['oneliner'])
            if new_oneliner:
                map_.oneliner = new_oneliner
        except:
            pass
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
                if is_default_username(username):
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
            data = json.dumps({'error': 'Could not make race for user/map combination'})
            return HttpResponse(data, content_type='application/json', status=400)

        try:
            map_ = Map.objects.get(pk=mid)
        except Map.DoesNotExist:
            data = json.dumps({'error': 'Could not find map with id {}'.format(mid)})
            return HttpResponse(data, content_type='application/json', status=400)

        try:
            # update player's statistics
            player.playtime += playtime
            player.races += races
            if created:
                player.maps += 1
            player.save()

            # update information for the race
            race.playtime += playtime
            race.last_played = timezone.now()
            race.set_points(-1)  # set negative points to indicate that this race is not yet processed
            race.save()

            raceh = RaceHistory.objects.create(
                player_id=player.id,
                map_id=mid,
                server=race.server,
                time=race.time,
                playtime=race.playtime,
                created=race.created,
                last_played=race.last_played)

            # trigger computation of points for this map in next scheduled task
            map_.compute_points = True
            map_.save()
        except:
            # TODO remove debug code
            import traceback
            traceback.print_exc()
            data = json.dumps({'error': 'Unexpected error..'})
            return HttpResponse(data, content_type='application/json', status=400)

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

        nickname = request.POST['nick']
        try:
            if is_default_username(nickname):
                data = {'error': 'Invalid nickname {}'.format(nickname)}
                status = 400

            else:
                player.name = request.POST['nick']
                player.simplified = strip_color_tokens( request.POST['nick'] )
                player.save()
                data = {player.name: True}
                status = 200

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
        except:
            data = json.dumps({'error': 'Invalid or missing parameter <map>'})
            return HttpResponse(data, content_type='application/json', status=400)

        try:
            limit = int(request.GET['limit'])
        except ValueError:
            data = json.dumps({'error': '<limit> should be a number'})
            return HttpResponse(data, content_type='application/json', status=400)
        except:
            data = json.dumps({'error': 'Invalid or missing parameter <limit>'})
            return HttpResponse(data, content_type='application/json', status=400)

        try:
            map_ = Map.objects.get(name=mapname)
        except:
            data = json.dumps({'error': 'Could not find map \'{}\''.format(mapname)})
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
            clear_oneliner = int(request.POST['co']) == 1
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

        if clear_oneliner:
            # remove old oneliner
            map_.oneliner = ""
            # trigger computation of points for this map in next scheduled task
            map_.compute_points = True
            map_.save()

        # No checks that the race is faster. That should be done on the gameserver
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
            created=race.created,
            last_played=race.last_played)

        # Update the record race
        race.set_points(-1)  # set negative points to indicate that this race is not yet processed
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


class APIRaceAll(View):
    """Server API interface for Race objects (new and old)."""

    def get(self, request):
        if not hasattr(request, 'server'):
            raise PermissionDenied

        try:
            mapname = base64.b64decode(request.GET['map'].encode('ascii'), '-_')
        except:
            data = json.dumps({'error': 'Invalid or missing parameter <map>'})
            return HttpResponse(data, content_type='application/json', status=400)

        try:
            limit = int(request.GET['limit'])
        except ValueError:
            data = json.dumps({'error': '<limit> should be a number'})
            return HttpResponse(data, content_type='application/json', status=400)
        except:
            data = json.dumps({'error': 'Invalid or missing parameter <limit>'})
            return HttpResponse(data, content_type='application/json', status=400)

        # 1.5
        try:
            map_ = Map.objects.get(name=mapname)
        except:
            data = json.dumps({'error': 'Could not find map \'{}\''.format(mapname)})
            return HttpResponse(data, content_type='application/json', status=400)

        # 1.0
        try:
            mapold_ = Mapold.objects.get(name=mapname)
        except:
            data = json.dumps({'error': 'Could not find 1.0 map \'{}\''.format(mapname)})
            return HttpResponse(data, content_type='application/json', status=400)

        # 1.5
        races = Race.objects.filter(map=map_, time__isnull=False).order_by('time')[:limit]

        # 1.0
        oldraces = PlayerMap.objects.filter(
            map=mapold_, time__isnull=False, player__isnull=False, prejumped='false').order_by('time')[:limit]

        data = {
            "map": mapname,
            "oneliner": map_.oneliner,
            "count": min(len(races) + len(oldraces), limit),
            "races": [],
            "oldoneliner": mapold_.oneliner,
            "oldraces": []
        }

        for race in races:
            srace = raceSerializer(race)
            srace['player'] = playerSerializer(race.player)
            del srace['playerId']
            data['races'].append(srace)

        for race in oldraces:
            srace = raceoldSerializer(race)
            srace['player'] = playeroldSerializer(race.player)
            data['oldraces'].append(srace)

        return HttpResponse(json.dumps(data), content_type='application/json')

    def post(self, request):
        raise Http404
