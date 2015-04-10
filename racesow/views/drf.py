import racesow.models as mod
import racesow.serializers as ser
from django.shortcuts import get_object_or_404
from racesow import utils
from rest_framework import viewsets
from rest_framework.response import Response


##########
# Mixins
##########


class B64Lookup(object):
    """Mixin class to lookup object on base64 encoded key"""

    def get_object(self):
        """Get the map specified for the detail view"""
        queryset = self.filter_queryset(self.get_queryset())

        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )

        lookup_value = utils.b64param(self.kwargs, lookup_url_kwarg)
        flt = {self.lookup_field: lookup_value}
        obj = get_object_or_404(queryset, **flt)
        self.check_object_permissions(self.request, obj)

        return obj


##########
# Views
##########


class PlayerViewSet(B64Lookup, viewsets.ModelViewSet):
    """ViewSet for players/ REST endpoint

    Routes:

    - List view: `players/`
    - Detail view: `players/{username}`

    Arguments:

    - `username` The player's warsow.net username as an urlsafe-base64
      encoded string

    Supported query parameters:

    - `sort={field}` Sort the results by the given field, prefix field with
      a "-" to reverse the sort.
    - `mid={id}` If provided, an extra "record" field will be added to the
      response data with the players best race on the map with `id`
    - `simplified={simplified}` Filter results to players whose simplified name
      matches. `simplified` must be a urlsafe-base64 encoded string.
    """
    lookup_field = 'username'
    queryset = mod.Player.objects.all()
    serializer_class = ser.PlayerSerializer
    ordering_fields = (
        'username', 'admin', 'simplified', 'playtime', 'races', 'maps',
        'maps_finished', 'points',
    )
    ordering = ('simplified',)

    def get_queryset(self):
        """Get the queryset for the players"""
        queryset = super(PlayerViewSet, self).get_queryset()

        if 'simplified' in self.request.query_params:
            value = utils.b64param(self.request.query_params, 'simplified')
            queryset = queryset.filter(simplified__iexact=value)

        return queryset

    def retrieve(self, request, *args, **kwargs):
        """Detail view for player

        This needs to be overridden to add record field.
        """
        instance = self.get_object()

        if 'mid' in request.query_params:
            flt = {
                'time__isnull': False,
                'map__id': request.query_params['mid']
            }
            try:
                instance.record = instance.race_set.get(**flt)
            except mod.Race.DoesNotExist:
                instance.record = None

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class MapViewSet(B64Lookup, viewsets.ModelViewSet):
    """ViewSet for maps/ REST endpoint

    Routes:

    - List view: `maps/`
    - Detail view: `maps/{name}/`

    Arguments:

    - `name` A urlsafe-base64 encoded string

    Supported query parameters:

    - `sort={field}` Sort the results by the given field, prefix field with
      a "-" to reverse the sort.
    - `rand` If supplied, the results will be randomly sorted, this takes
      precedence over `sort`
    - `pattern={pattern}` Filter the results to maps with names matching a
      regex pattern. `pattern` must be a urlsafe-base64 encoded string.
    - `tags={tags}` Filter the results to maps with every tag in `tags`.
      `tags` must be a urlsafe-base64 encoded json list. E.g.
      `["pg", "rl"]`
    """
    lookup_field = 'name'
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
