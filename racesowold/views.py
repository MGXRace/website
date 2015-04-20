"""Racesow Old Models View"""
import base64
import json
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.views.generic import View
from racesowold import models, serializers


def _b64decode(msg):
    return base64.b64decode(msg.encode('ascii'), '-_')


class APIRace(View):
    """Server API interface for Race objects."""

    def get(self, request):
        if not hasattr(request, 'server'):
            raise PermissionDenied

        try:
            mapname = _b64decode(request.GET['map'])
        except:
            data = json.dumps({'error': 'Invalid or missing parameter <map>'})
            return HttpResponse(data, content_type='application/json',
                                status=400)

        try:
            limit = int(request.GET['limit'])
        except ValueError:
            data = json.dumps({'error': '<limit> should be a number'})
            return HttpResponse(data, content_type='application/json',
                                status=400)
        except:
            data = json.dumps(
                {'error': 'Invalid or missing parameter <limit>'})
            return HttpResponse(data, content_type='application/json',
                                status=400)

        try:
            map_ = models.Map.objects.get(name=mapname)
        except:
            data = json.dumps(
                {'error': 'Could not find map \'{}\''.format(mapname)})
            return HttpResponse(data, content_type='application/json',
                                status=400)

        flt = {
            'map': map_,
            'time__isnull': False,
            'player__isnull': False,
            'prejumped': 'false',
        }
        races = models.PlayerMap.objects.filter(**flt).order_by('time')[:limit]
        data = {
            "map": mapname,
            "oneliner": map_.oneliner,
            "count": len(races),
            "races": []
        }

        for race in races:
            srace = serializers.raceSerializer(race)
            srace['player'] = serializers.playerSerializer(race.player)
            data['races'].append(srace)

        return HttpResponse(json.dumps(data), content_type='application/json')
