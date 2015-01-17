import json
from django.db.models import Min
from django.http import HttpResponse, Http404
from django.views.generic import View
from racesow.models import Player, Race
from racesow.serializers import playerSerializer

__author__ = 'Mark'


class MatchMaker(View):
    def get(self, request, **kwargs):
        # This is experimental and will probably be removed.

        try:
            username = kwargs['username']
            player_ = Player.objects.get(username=username)
        except:
            data = json.dumps({'error': 'Player not found'})
            return HttpResponse(data, content_type='application_json', status=404)

        records_all = Race.objects.filter(time__isnull=False).values('map_id').annotate(besttime=Min('time'))
        races_name = Race.objects.filter(player__pk=player_.pk, time__isnull=False)

        try:
            firstplaces = 0
            for race in races_name:
                mapid = race.map.pk
                maptime = int(race.time)
                for record in records_all:
                    if record['map_id'] == mapid and record['besttime'] == maptime:
                        firstplaces += 1
        except:
            import traceback
            print "Error in MatchMaker calculations!"
            print "\nrecords_all: {}\nraces_name: {}".format(records_all, races_name)
            traceback.print_exc()
            data = json.dumps({'error': 'exception'})
            return HttpResponse(data, content_type='application_json', status=404)

        # Serialize the player
        pdata = playerSerializer(player_)
        data = {'playtime_sec': int(pdata['playtime']/1000.0),
                'maps': pdata['maps'],
                'records': firstplaces}
        return HttpResponse(json.dumps(data), content_type='application/json')

    def post(self, request):
        raise Http404