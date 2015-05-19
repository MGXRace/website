from django.http import QueryDict
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers, fields
from racesow.models import Player, Map, Tag, Race, Checkpoint


class AddFieldSerializer(object):
    """Mixin class to support increment fields

    Fields named `basefield_add` will have their value added to `basefield`
    before saving. Fields for addition must be declared in `Meta.add_fields`.
    """

    def _process_add_fields(self, validated_data, instance=None):
        """Calculate new field values from an instance and the field_add values

        This modifies validated_data in place.
        """
        for field in self.Meta.add_fields:
            add_field = field + '_add'
            if add_field not in validated_data:
                continue

            add_value = validated_data.pop(add_field)

            base_value = 0
            if field in validated_data:
                base_value = validated_data[field]
            else:
                base_value = getattr(instance, field, 0)

            validated_data[field] = base_value + add_value

        return validated_data

    def create(self, validated_data):
        validated_data = self._process_add_fields(validated_data)
        return super(AddFieldSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        validated_data = self._process_add_fields(validated_data, instance)
        return super(AddFieldSerializer, self).update(instance, validated_data)


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


class RaceSerializer(AddFieldSerializer, serializers.ModelSerializer):
    playtime_add = serializers.IntegerField(write_only=True, required=False)
    races_add = serializers.IntegerField(write_only=True, required=False)
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
            'playtime_add',
            'races_add',
            'points',
            'created',
            'checkpoints',
        )
        add_fields = ('playtime', 'races')

    def __init__(self, instance=None, data=fields.empty, **kwargs):
        # Workaround for http://stackoverflow.com/questions/29759838/
        if isinstance(data, QueryDict):
            data = dict(data.items())

        super(RaceSerializer, self).__init__(instance, data, **kwargs)

    def set_checkpoints(self, instance, checkpoint_data):
        if checkpoint_data is None:
            return

        instance.checkpoints.all().delete()
        Checkpoint.objects.bulk_create([
            Checkpoint(race=instance, **d) for d in checkpoint_data
        ])

    def update_map(self, instance):
        record = Race.objects.filter(map=instance.map, time__isnull=False) \
                             .order_by('time')[:1]

        if instance.time is not None:
            instance.map.compute_points = True
        if record and record[0].pk == instance.pk:
            instance.map.oneliner = ''
        instance.map.save()

    def create(self, validated_data):
        checkpoint_data = validated_data.pop('checkpoints', None)
        instance = super(RaceSerializer, self).create(validated_data)
        self.set_checkpoints(instance, checkpoint_data)
        self.update_map(instance)

        instance.player.maps += 1
        if validated_data.get('time', None) is not None:
            instance.player.maps_finished += 1
        instance.player.save()

        return instance

    def update(self, instance, validated_data):
        checkpoint_data = validated_data.pop('checkpoints', None)
        increment_maps_finished = (validated_data.get('time', None) is not None
                                   and instance.time is None)

        instance = super(RaceSerializer, self).update(instance, validated_data)
        self.set_checkpoints(instance, checkpoint_data)
        self.update_map(instance)

        if increment_maps_finished:
            instance.player.maps_finished += 1
            instance.player.save()

        return instance


class PlayerSerializer(AddFieldSerializer, serializers.ModelSerializer):
    playtime_add = serializers.IntegerField(write_only=True, required=False)
    races_add = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Player
        fields = (
            'id',
            'username',
            'admin',
            'name',
            'simplified',
            'playtime',
            'playtime_add',
            'races',
            'races_add',
            'maps',
            'maps_finished',
            'points',
        )
        add_fields = ('playtime', 'races')


class MapSerializer(AddFieldSerializer, serializers.ModelSerializer):
    playtime_add = serializers.IntegerField(write_only=True, required=False)
    races_add = serializers.IntegerField(write_only=True, required=False)
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
            'races_add',
            'oneliner',
            'playtime',
            'playtime_add',
            'created',
            'tags',
            'record',
        )
        add_fields = ('playtime', 'races')


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
