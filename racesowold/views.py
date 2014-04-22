"""
Racesow Old Models View
"""
import base64
import json
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.views.generic import View
from .models import (
    Map,
    PlayerMap)
from .serializers import (
    playerSerializer,
    raceSerializer)


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

        races = PlayerMap.objects.filter(map=map_,
                                         time__isnull=False,
                                         player__isnull=False)\
                                 .order_by('time')[:limit]
        data = {
            "map": mapname,
            "oneliner": map_.oneliner,
            "count": len(races),
            "races": []
        }

        for race in races:
            srace = raceSerializer(race)
            srace['player'] = playerSerializer(race.player)
            data['races'].append(srace)

        return HttpResponse(json.dumps(data), content_type='application/json')
