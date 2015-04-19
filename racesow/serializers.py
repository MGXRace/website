from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from racesow.models import Player, Map, Tag, Race, Checkpoint


class LiteSerializer(serializers.ModelSerializer):
    """A Serializer which reads as an object, but writes as pk"""
    default_error_messages = {
        'required': _('This field is required.'),
        'does_not_exist': _('Invalid pk "{pk_value}" - object does not'
                            ' exist.'),
        'incorrect_type': _('Incorrect type. Expected pk value, received'
                            ' {data_type}.'),
    }

    def to_internal_value(self, data):
        ModelClass = self.Meta.model

        try:
            return ModelClass.objects.get(pk=data)
        except ModelClass.DoesNotExist:
            self.fail('does_not_exist', pk_value=data)
        except (TypeError, ValueError):
            self.fail('incorrect_type', data_type=type(data).__name__)


class PlayerLiteSerializer(LiteSerializer):
    """Minimal serializer for Player model

    Intended to nest Players in other serializers.
    """

    class Meta:
        model = Player
        fields = (
            'id',
            'name',
            'simplified',
        )


class CheckpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checkpoint
        fields = (
            'id',
            'number',
            'time',
        )


class RaceSerializer(serializers.ModelSerializer):
    player = PlayerLiteSerializer()
    checkpoints = CheckpointSerializer(many=True, partial=True)

    class Meta:
        model = Race
        fields = (
            'id',
            'player',
            'map',
            'server',
            'time',
            'playtime',
            'points',
            'created',
            'checkpoints',
        )

    def set_checkpoints(self, instance, checkpoint_data):
        if checkpoint_data is None:
            return

        instance.checkpoints.all().delete()
        Checkpoint.objects.bulk_create([
            Checkpoint(race=instance, **d) for d in checkpoint_data
        ])

    def create(self, validated_data):
        checkpoint_data = validated_data.pop('checkpoints', None)
        instance = super(RaceSerializer, self).create(validated_data)
        self.set_checkpoints(instance, checkpoint_data)
        return instance

    def update(self, instance, validated_data):
        checkpoint_data = validated_data.pop('checkpoints', None)
        instance = super(RaceSerializer, self).update(instance, validated_data)
        self.set_checkpoints(instance, checkpoint_data)
        return instance


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
    record = RaceSerializer(read_only=True)

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
            'record',
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

    pk3file = map_.pk3file.url if map_.pk3file else None
    levelshotfile = map_.levelshotfile.url if map_.levelshotfile else None
    return {
        'id': map_.id,
        'name': map_.name,
        'pk3file': pk3file,
        'levelshotfile': levelshotfile,
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

    cp_set = race.checkpoints.all()

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
