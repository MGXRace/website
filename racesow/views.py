import base64
import json
from .models import (
    Tag,
    Map,
    Server,
    Race,
    Checkpoint,
    Player)
from .serializers import (
    mapSerializer,
    raceSerializer)


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