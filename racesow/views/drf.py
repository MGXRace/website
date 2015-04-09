import racesow.models as mod
import racesow.serializers as ser
from racesow import utils
from rest_framework import viewsets


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = mod.Player.objects.all()
    serializer_class = ser.PlayerSerializer


class MapViewSet(viewsets.ModelViewSet):
    queryset = mod.Map.objects.all()
    serializer_class = ser.MapSerializer
    ordering_fields = ('name', 'races', 'playtime', 'created', 'oneliner')
    ordering = ('name',)

    def get_queryset(self):
        """Generate the queryset of map objects for the given params"""
        queryset = mod.Map.objects.filter(enabled=True)

        if self.request.query_params.get('pattern', None):
            pattern = utils.b64param(self.request.query_params, 'pattern')
            queryset = queryset.filter(name__regex=pattern)

        if self.request.query_params.get('tags', None):
            tags = utils.jsonparam(self.request.query_params, 'tags')
            for tag in tags:
                queryset = queryset.filter(tags__name__iexact=tag)

        return queryset

    def filter_queryset(self, queryset):
        """Apply filter backends to the queryset

        This needs to be overridden to apply a random sort
        """
        queryset = super(MapViewSet, self).filter_queryset(queryset)

        if 'rand' in self.request.query_params:
            queryset = queryset.order_by('?')
        return queryset


class TagViewSet(viewsets.ModelViewSet):
    lookup_field = 'name'
    queryset = mod.Tag.objects.all()
    serializer_class = ser.TagSerializer
    ordering_fields = ('name',)
    ordering = ('name',)


class RaceViewSet(viewsets.ModelViewSet):
    queryset = mod.Race.objects.all()
    serializer_class = ser.RaceSerializer


class CheckpointViewSet(viewsets.ModelViewSet):
    queryset = mod.Checkpoint.objects.all()
    serializer_class = ser.CheckpointSerializer
