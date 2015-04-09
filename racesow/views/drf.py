import racesow.models as mod
import racesow.serializers as ser
from django.shortcuts import get_object_or_404
from racesow import utils
from rest_framework import viewsets


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


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = mod.Player.objects.all()
    serializer_class = ser.PlayerSerializer


class MapViewSet(B64Lookup, viewsets.ModelViewSet):
    """ViewSet for maps/ REST endpoint

    Routes:

    - List view: `apiroot/maps/`
    - Detail view: `apiroot/maps/{mapname}/`

    Arguments:

    - `mapname` A urlsafe-base64 encoded string

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
