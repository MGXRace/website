from django.utils import timezone
from rest_framework import serializers, viewsets
from racesow.models import Player, Map, Tag


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = (
            'id',
            'username',
            'admin',
            'name',
            'simplified',
            'playtime',
            'races',
            'maps',
            'maps_finished',
            'points',
        )


class MapSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Tag.objects.all(),
    )

    class Meta:
        model = Map
        fields = (
            'id',
            'name',
            'pk3file',
            'levelshotfile',
            'enabled',
            'races',
            'oneliner',
            'playtime',
            'created',
            'tags',
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'name',
        )


def playerSerializer(player):
    """
    Formats a player object into primitive types for serializing

    Outputs in the form
    ```
    {
        "id": 1,
        "admin": false,
        "name": "^1Awesome ^4Racer",
        "simplified": "Awesome Racer",
        "playtime": 30,
        "races": 10,
        "maps": 2,
        "points": 68,
        "skill": 32.8,
    }
    ```
    """
    return {
        'id': player.id,
        'username': player.username,
        'admin': player.admin,
        'name': player.name,
        'simplified': player.simplified,
        'playtime': player.playtime,
        'races': player.races,
        'maps': player.maps
    }


def mapSerializer(map_):
    """
    Formats a map object into primitive types for serializing

    Outputs in the form
    ```
    {
        "id": 1,
        "name": "coldrun",
        "pk3file": "http://www.example.com/pk3/coldrun.pk3",
        "levelshotfile": "http://www.example.com/ls/coldrun.jpg",
        "enabled": true,
        "races": 5,
        "playtime": 30,
        "created": "YYYY-MM-DDTHH:MM:SSZ",
        "tags": ["rl", "pg"]
    }
    ```
    """
    created = map_.created
    if timezone.is_aware(created):
        created = timezone.localtime(created, timezone=timezone.utc)

    return {
        'id': map_.id,
        'name': map_.name,
        'pk3file': map_.pk3file.url if map_.pk3file else None,
        'levelshotfile': map_.levelshotfile.url if map_.levelshotfile else None,
        'enabled': map_.enabled,
        'races': map_.races,
        'oneliner': map_.oneliner,
        'playtime': map_.playtime,
        'created': created.isoformat() + 'Z',
        'tags': [tag.name for tag in map_.tags.all()]
    }


def raceSerializer(race):
    """
    Formats a race object into primitive types for serializing

    Outputs in the form
    ```
    {
        "id": 1,
        "playerId": 3,
        "mapId": 7,
        "serverId": null,
        "time": 30295,
        "playtime": 129841,
        "points": 30.59,
        "created": "YYYY-MM-DD"
        "checkpoints": [1243, 3428945, 0, 0, 18934255]
    }
    ```
    """
    created = race.created
    if timezone.is_aware(created):
        created = timezone.localtime(created, timezone=timezone.utc)

    cp_set = race.checkpoint_set.all()

    return {
        'id': race.id,
        'playerId': race.player_id,
        'mapId': race.map_id,
        'serverId': race.server_id,
        'time': race.time,
        'playtime': race.playtime,
        'points': race.get_points(),
        'created': created.strftime("%Y-%m-%d - %H:%M:%S"),
        'checkpoints': [checkpointSerializer(cp) for cp in cp_set]
    }


def checkpointSerializer(checkpoint):
    """
    Formats a checkpoint into primitive types

    Outputs in the form
    ```
    {
        "id": 1,
        "raceId": 1,
        "number": 3,
        "time": 93814
    }
    ```
    """
    return {
        'id': checkpoint.id,
        'raceId': checkpoint.race_id,
        'number': checkpoint.number,
        'time': checkpoint.time
    }
