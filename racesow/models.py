from django.db import models
from django.conf import settings
from django.utils import timezone
_null = {'blank': True, 'null': True, 'default': None}

class Tag(models.Model):
    """Tag for describing a map

    Model Fields:
        name (str): Name of the tag
    """
    name = models.CharField(max_length=15)

    def __unicode__(self):
        return self.name


class Server(models.Model):
    """Racesow Server Model

    Model Fields:
        user (User): User who owns/operates the server
        auth_key (str): Server authentication key for generating api tokens
        address (str): The server address in the form "(ip|domain):port"
        name (str): Name of the server (its sv_hostname setting)
        simplified (str): Name of the server without color codes
        playtime (int): Time played on server in (milli?)seconds
        races (int): Number of races finished on the server
        created (datetime): Date/time the server was created
        last_seen (datetime): Date/time the server last phoned home
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, **_null)
    auth_key = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    simplified = models.CharField(max_length=255)
    players = models.TextField(blank=True)
    playtime = models.BigIntegerField(default=0)
    races = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(default=timezone.now)
    last_seen = models.DateTimeField(**_null)

    def __unicode__(self):
        return self.simplified


class Map(models.Model):
    """Racesow Map Model

    Model Fields:
        name (str): Name of the map
        pk3file (File): File object of the map pk3
        levelshotfile (File): File object of the levelshot image
        enabled (bool): True if the map is enabled
        races (int): Number of completed races
        playtime (int): Playtime on the map in seconds
        created (datetime): Datetime map was added
        oneliner (str): Oneliner message for the map
        tags (RelatedManager): Manager for Tag objects associated with the map
    """
    name = models.CharField(max_length=255)
    pk3file = models.FileField(upload_to='maps', blank=True)
    levelshotfile = models.FileField(upload_to='levelshots', blank=True)
    enabled = models.BooleanField(default=True)
    races = models.IntegerField(default=0)
    playtime = models.BigIntegerField(default=0)
    created = models.DateTimeField(default=timezone.now)
    oneliner = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField(Tag)

    def __unicode__(self):
        return self.name


class MapRating(models.Model):
    """Racesow Map Rating Model

    Model Fields:
        user (User): User who set the rating
        map (Map): Map rated
        rating (int): Rating value given
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    map = models.ForeignKey(Map)
    rating = models.IntegerField()

    def __unicode__(self):
        return '<User: {0}, Map: {1}, Rating: {2}>'.format(self.user, self.map,
                                                           self.rating)

    class Meta:
        unique_together = ('user', 'map')


class PlayerHistory(models.Model):
    """Racesow Player History Model

    Model Fields:
        user (User): User associated with the player
        name (str): racesow username with colorcodes
        simplified (str): racesow username without colorcodes
        playtime (int): player's ingame playtime in seconds
        races (int): number of races the player has finished
        maps (int): number of maps the player has finished a race on
        points (int): points the player has
        skill_m (float): player's skill rating (mu)
        skill_s (float): uncertainty in player's skill rating (sigma)
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, unique=True,
                             on_delete=models.SET_NULL, **_null)
    name = models.CharField(max_length=64)
    simplified = models.CharField(max_length=64, unique=True)
    playtime = models.BigIntegerField(default=0)
    races = models.IntegerField(default=0)
    maps = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    skill_m = models.FloatField(default=0)
    skill_s = models.FloatField(default=1)

    def __unicode__(self):
        if self.user:
            return '<Player user:{}>'.format(self.user.get_username())
        return '<Player name:{}>'.format(self.simplified)


class Player(models.Model):
    """Racesow Player Model

    Model Fields:
        user (User): User associated with the player
        admin (bool): True if the player has ingame admin privleges
        name (str): racesow username with colorcodes
        simplified (str): racesow username without colorcodes
        playtime (int): player's ingame playtime in seconds
        races (int): number of races the player has finished
        maps (int): number of maps the player has completed a race on
        points (int): points the player has
        skill_m (float): player's skill rating (mu)
        skill_s (float): uncertainty in player's skill rating (sigma)
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, unique=True,
                             on_delete=models.SET_NULL, **_null)
    admin = models.BooleanField(default=False)
    name = models.CharField(max_length=64)
    simplified = models.CharField(max_length=64, unique=True)
    playtime = models.BigIntegerField(default=0)
    races = models.IntegerField(default=0)
    maps = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    skill_m = models.FloatField(default=0)
    skill_s = models.FloatField(default=1)

    def __unicode__(self):
        if self.user:
            return '<Player user:{}>'.format(self.user.get_username())
        return '<Player name:{}>'.format(self.simplified)


class RaceHistory(models.Model):
    """Racesow Race History Model

    Model Fields:
        player (Player): Player performing the race
        map (Map): Map the race was performed on
        server (Server): Server the race was performed on
        time (int): Time to complete the race in milliseconds
        points (int): Points assigned to the record at the time of creation
        playtime (int): Player's cumulative playtime on the map
        created (datetime): Datetime when the record was made
        last_played (datetime): Datetime when the playtime stats were updated
    """
    player = models.ForeignKey(Player)
    map = models.ForeignKey(Map)
    server = models.ForeignKey(Server, on_delete=models.SET_NULL, **_null)
    time = models.IntegerField(**_null)
    points = models.IntegerField(default=0)
    playtime = models.BigIntegerField(default=0)
    created = models.DateTimeField(default=timezone.now)
    last_played = models.DateTimeField(default=timezone.now)

    def __unicode__(self):
        return 'player: {}, map: {}, time: {}'.format(self.player.simplified,
                                                      self.map.name, self.time)


class Race(models.Model):
    """Racesow Race Model

    This is identical to the Race History Model, except it is unique on
    (player, map) containing only the latest / best records for each
    player-map pair.

    Model Fields:
        player (Player): Player performing the race
        map (Map): Map the race was performed on
        server (Server): Server the race was performed on
        time (int): Time to complete the race in milliseconds
        points (int): Points assigned to the record at the time of creation
        playtime (int): Player's cumulative playtime on the map
        created (datetime): Datetime when the record was made
        last_played (datetime): Datetime when the playtime stats were updated
    """
    player = models.ForeignKey(Player)
    map = models.ForeignKey(Map)
    server = models.ForeignKey(Server, on_delete=models.SET_NULL, **_null)
    time = models.IntegerField(**_null)
    points = models.IntegerField(default=0)
    playtime = models.BigIntegerField(default=0)
    created = models.DateTimeField(default=timezone.now)
    last_played = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('player', 'map')

    def __unicode__(self):
        return 'player: {}, map: {}, time: {}'.format(self.player.simplified,
                                                      self.map.name, self.time)


class Checkpoint(models.Model):
    """Racesow Checkpoint Model

    Contains the checkpoints for a players race entry

    Model Fields:
        race (Race): Race the checkpoints are associated with
        number (int): Number of the checkpoint
        time (int): Time of the race that the checkpoint was touched
    """
    race = models.ForeignKey(Race)
    number = models.IntegerField()
    time = models.IntegerField()

    class Meta:
        unique_together = ('race', 'number')

    def __unicode__(self):
        return '<player: {}, map: {}, cpNum: {}>'.format(
            self.race.player.simplified, self.race.map.name, self.number)
