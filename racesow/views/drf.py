import racesow.models as models
import racesow.serializers as serializers
import racesowold.models as models_10
import racesowold.serializers as serializers_10
from django.http import Http404
from django.shortcuts import get_object_or_404
from racesow import utils
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.request import clone_request


##########
# Mixins
##########


class B64Lookup(object):
    """Mixin class to lookup object on base64 encoded key"""

    def lookup_filter(self):
        """Decode the lookup value from url kwargs"""
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )
        lookup_value = utils.b64param(self.kwargs, lookup_url_kwarg)
        return {self.lookup_field: lookup_value}

    def get_object(self):
        """Get the map specified for the detail view"""
        queryset = self.filter_queryset(self.get_queryset())
        obj = get_object_or_404(queryset, **self.lookup_filter())
        self.check_object_permissions(self.request, obj)

        return obj


class UpdateOrCreate(object):
    """Mixin class to update or create an object for PUT|PATCH requests"""

    def update(self, request, *args, **kwargs):
        """Update the object"""
        serializer, created = self.update_or_create(request, *args, **kwargs)
        self.perform_update(serializer)

        if created:
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.data)

    def update_or_create(self, request, *args, **kwargs):
        """Return the updated serializer for the request"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object_or_none()
        data = request.data.copy()
        created = False

        if instance is None:
            created = True

            try:
                value = self.lookup_filter()
            except AttributeError:
                lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
                value = {self.lookup_field: self.kwargs[lookup_url_kwarg]}

            value.update(data)
            data = value

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)

        return serializer, created

    def get_object_or_none(self):
        """Return the object for the request or none"""
        try:
            return self.get_object()
        except Http404:
            if self.request.method in ('PUT', 'PATCH'):
                self.check_permissions(clone_request(self.request, 'POST'))
            else:
                raise


class RaceMixin(object):
    """Mixin class for race views"""

    def lookup_filter(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        try:
            mappk, playerpk = self.kwargs[lookup_url_kwarg].split(';')
        except ValueError:
            raise Http404
        return {'map': mappk, 'player': playerpk}

    def get_queryset(self):
        """Get the queryset for the races"""
        queryset = super(RaceMixin, self).get_queryset()

        mpk = self.request.query_params.get('map', None)
        if mpk:
            mpk = utils.clean_pk(models.Map, mpk, 'Invalid map key: {0}')
            queryset = queryset.filter(map__pk=mpk)

        ppk = self.request.query_params.get('player', None)
        if ppk:
            ppk = utils.clean_pk(models.Player, ppk, 'Invalid player key: {0}')
            queryset = queryset.filter(player__pk=ppk)

        return queryset

    def get_object(self):
        """Get the object for races from a player/map composite key"""
        queryset = self.filter_queryset(self.get_queryset())
        obj = get_object_or_404(queryset, **self.lookup_filter())
        self.check_object_permissions(self.request, obj)

        return obj


##########
# Views
##########


class PlayerViewSet(B64Lookup, UpdateOrCreate, viewsets.ModelViewSet):
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
    queryset = models.Player.objects.all()
    serializer_class = serializers.PlayerSerializer
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

    def set_record(self, data, request, player):
        """Get the player's race for a given map"""
        if 'mid' not in request.query_params:
            return

        mappk = request.query_params['mid']
        try:
            record = player.race_set.get(map=mappk)
        except models.Race.DoesNotExist:
            data['record'] = None
            return
        data['record'] = serializers.RaceSerializer(record).data

    def retrieve(self, request, *args, **kwargs):
        """Detail view for player

        This needs to be overridden to add record field.
        """
        instance = self.get_object()
        data = self.get_serializer(instance).data
        self.set_record(data, request, instance)
        return Response(data)

    def update(self, request, *args, **kwargs):
        """Update the player"""
        serializer, created = self.update_or_create(request, *args, **kwargs)
        instance = serializer.save()
        data = serializer.data
        self.set_record(data, request, instance)

        if created:
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(data)


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
    - `record` If supplied on a detail view, the result will have a `record`
      field with the best race on the map.
    - `pattern={pattern}` Filter the results to maps with names matching a
      regex pattern. `pattern` must be a urlsafe-base64 encoded string.
    - `tags={tags}` Filter the results to maps with every tag in `tags`.
      `tags` must be a urlsafe-base64 encoded json list. E.g.
      `["pg", "rl"]`
    """
    lookup_field = 'name'
    queryset = models.Map.objects.all()
    serializer_class = serializers.MapSerializer
    ordering_fields = ('name', 'races', 'playtime', 'created', 'oneliner')
    ordering = ('name',)

    def get_queryset(self):
        """Generate the queryset of map objects for the given params"""
        queryset = models.Map.objects.filter(enabled=True)

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

    def retrieve(self, request, *args, **kwargs):
        """Detail view for map

        This needs to be overridden to add record field.
        """
        instance = self.get_object()

        if 'record' in request.query_params:
            record = instance.race_set \
                             .filter(time__isnull=False) \
                             .order_by('time')[:1]
            if record:
                instance.record = record[0]
            else:
                instance.record = None

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    lookup_field = 'name'
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer
    ordering_fields = ('name',)
    ordering = ('name',)


class RaceViewSet(RaceMixin, UpdateOrCreate, viewsets.ModelViewSet):
    """ViewSet for races/ REST endpoint

    Routes:

    - List view: `races/`
    - Detail view: `races/{mappk};{playerpk}/`

    Arguments:

    - `mappk` id of the map
    - `playerpk` id of the player

    Supported query parameters:

    - `sort={field}` Sort the results by the given field, prefix field with
      a "-" to reverse the sort.
    - `map={pk}` Filter results to races on a specific map
    - `player={pk}` Filter results to races by a specific player
    """
    queryset = models.Race.objects.all()
    serializer_class = serializers.RaceSerializer
    ordering_fields = (
        'player__simplified', 'map__name', 'server__name', 'time', 'playtime',
        'points', 'rank', 'created', 'last_played',
    )
    ordering = ('time',)


class CheckpointViewSet(viewsets.ModelViewSet):
    queryset = models.Checkpoint.objects.all()
    serializer_class = serializers.CheckpointSerializer


class Race10ViewSet(RaceMixin, viewsets.ReadOnlyModelViewSet):
    """ViewSet for races-10/ REST endpoint

    Routes:

    - List view: `races-10/`
    - Detail view: `races-10/{mappk};{playerpk}/`

    Arguments:

    - `mappk` id of the map
    - `playerpk` id of the player

    Supported query parameters:

    - `sort={field}` Sort the results by the given field, prefix field with
      a "-" to reverse the sort.
    - `map={pk}` Filter results to races on a specific map
    - `player={pk}` Filter results to races by a specific player
    """
    queryset = models_10.PlayerMap.objects.filter(
        map__isnull=False,
        player__isnull=False,
        time__isnull=False,
        prejumped='false'
    )
    serializer_class = serializers_10.RaceSerializer
    ordering_fields = (
        'player__simplified', 'map__name', 'server__servername', 'time',
        'playtime', 'points', 'created',
    )
    ordering = ('time',)
