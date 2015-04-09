from rest_framework import viewsets
import racesow.models as mod
import racesow.serializers as ser


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = mod.Player.objects.all()
    serializer_class = ser.PlayerSerializer


class MapViewSet(viewsets.ModelViewSet):
    queryset = mod.Map.objects.all()
    serializer_class = ser.MapSerializer


class TagViewSet(viewsets.ModelViewSet):
    lookup_field = 'name'
    queryset = mod.Tag.objects.all()
    serializer_class = ser.TagSerializer


class RaceViewSet(viewsets.ModelViewSet):
    queryset = mod.Race.objects.all()
    serializer_class = ser.RaceSerializer


class CheckpointViewSet(viewsets.ModelViewSet):
    queryset = mod.Checkpoint.objects.all()
    serializer_class = ser.CheckpointSerializer
