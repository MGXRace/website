from django.utils import timezone

def playerSerializer(player):
    """
    Formats an old player object into primitive types for serializing

    Outputs in the form
    ```
    {
        "id": 1,
        "name": "^1Awesome ^4Racer",
        "simplified": "Awesome Racer",
        "playtime": 30,
        "races": 10,
        "maps": 2,
        "points": 68,
    }
    ```
    """
    return {
        'id': player.id,
        'name': player.name,
        'simplified': player.simplified,
        'playtime': player.playtime,
        'races': player.races,
        'maps': player.maps,
        'points': player.points
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
    if created and timezone.is_aware( created ):
        created = timezone.localtime(created, timezone=timezone.utc).isoformat()

    return {
        'id': map_.id,
        'name': map_.name,
        'status': map_.status,
        'races': map_.races,
        'oneliner': map_.oneliner,
        'playtime': map_.playtime,
        'created': created
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
        "points": 40,
        "playtime": 129841,
        "created": "YYYY-MM-DD"
        "checkpoints": [1243, 3428945, 0, 0, 18934255]
    }
    ```
    """
    created = race.created
    if not created:
        created = '0000-00-00'
    elif timezone.is_aware( created ):
        created = timezone.localtime(created, timezone=timezone.utc) \
                          .strftime('%Y-%m-%d')

    return {
        'id': race.id,
        'playerId': race.player_id,
        'mapId': race.map_id,
        'serverId': race.server_id,
        'time': race.time,
        'points': race.points,
        'playtime': race.playtime,
        'created': created
    }
