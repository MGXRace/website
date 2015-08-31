import datetime

from django.db import models
from django.utils import timezone

from racesow.utils import username_with_html_colors, millis_to_str


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
        user (Player): Player who owns/operates the server
        auth_key (str): Server authentication key for generating api tokens
        address (str): The server address in the form "(ip|domain):port"
        name (str): Name of the server (its sv_hostname setting)
        simplified (str): Name of the server without color codes
        playtime (int): Time played on server in (milli?)seconds
        races (int): Number of races finished on the server
        created (datetime): Date/time the server was created
        last_seen (datetime): Date/time the server last phoned home
    """
    user = models.ForeignKey('Player', on_delete=models.SET_NULL, **_null)
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
        name (str): Name of the map (unique)
        pk3file (File): File object of the map pk3
        levelshotfile (File): File object of the levelshot image
        enabled (bool): True if the map is enabled
        races (int): Number of completed races
        playtime (int): Playtime on the map in seconds
        created (datetime): Datetime map was added
        oneliner (str): Oneliner message for the map
        tags (RelatedManager): Manager for Tag objects associated with the map
        compute_points (bool): True if the map has new race times or playtimes
        last_computation (datetime): last computation of points for races on this map
    """
    name = models.CharField(max_length=255, unique=True)
    pk3file = models.FileField(upload_to='maps', blank=True)
    levelshotfile = models.FileField(upload_to='levelshots', blank=True)
    enabled = models.BooleanField(default=True)
    races = models.IntegerField(default=0)
    playtime = models.BigIntegerField(default=0)
    created = models.DateTimeField(default=timezone.now)
    oneliner = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField(Tag)
    compute_points = models.BooleanField(default=False)
    last_computation = models.DateTimeField(default=timezone.now)

    def __unicode__(self):
        return self.name

    def playtime_formatted(self):
        return datetime.timedelta(seconds=int(self.playtime) / 1000)

    def get_tags(self):
        return ", ".join([x.name for x in self.tags.all()])
    get_tags.short_description = 'Tags'


class MapRating(models.Model):
    """Racesow Map Rating Model

    Model Fields:
        user (Player): Player who set the rating
        map (Map): Map rated
        rating (int): Rating value given
    """
    user = models.ForeignKey('Player')
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
        username (str): Warsow.net username associated with the player
        name (str): racesow username with colorcodes
        simplified (str): racesow username without colorcodes
        playtime (int): player's ingame playtime in seconds
        races (int): number of races the player has finished
        maps (int): number of maps the player has finished a race on
    """
    username = models.CharField(max_length=64)
    name = models.CharField(max_length=64)
    simplified = models.CharField(max_length=64, unique=True)
    playtime = models.BigIntegerField(default=0)
    races = models.IntegerField(default=0)
    maps = models.IntegerField(default=0)

    def __unicode__(self):
        if self.user:
            return '<Player user:{}>'.format(self.user.get_username())
        return '<Player name:{}>'.format(self.simplified)


class Player(models.Model):
    """Racesow Player Model

    Model Fields:
        username (str): Warsow.net username associated with the player
        admin (bool): True if the player has ingame admin privleges
        name (str): racesow username with colorcodes
        simplified (str): racesow username without colorcodes
        playtime (int): player's ingame playtime in seconds
        races (int): number of races the player has finished
        maps (int): number of maps the player has raced on
        maps_finished (int): number of maps the player has completed a race on
        points (int): total number of point this player has earned, in thousands

    """
    username = models.CharField(max_length=64, unique=True)
    admin = models.BooleanField(default=False)
    name = models.CharField(max_length=64)
    simplified = models.CharField(max_length=64, unique=True)
    playtime = models.BigIntegerField(default=0)
    races = models.IntegerField(default=0)
    maps = models.IntegerField(default=0)
    maps_finished = models.IntegerField(default=0)  # for tracking actually finished maps
    points = models.IntegerField(default=0)         # total number of points

    def __unicode__(self):
        return '<Player user:{}, nick:{}>'.format(self.username,
                                                  self.simplified)

    def htmlname(self):
        return username_with_html_colors(u'{}'.format(self.name))

    def playtime_formatted(self):
        return millis_to_str(int(self.playtime))

    def get_points(self):
        # transform points back to float with 3 decimals
        return float(self.points / 1000.0)

    def set_points(self, points):
        # keeps 3 decimals by multiplying with 1000
        self.points = int(points * 1000)

    def add_points(self, points):
        # keeps 3 decimals by multiplying with 1000
        self.points += int(points * 1000)


class RaceHistory(models.Model):
    """Racesow Race History Model

    Model Fields:
        player (Player): Player performing the race
        map (Map): Map the race was performed on
        server (Server): Server the race was performed on
        time (int): Time to complete the race in milliseconds (null if no time was made)
        playtime (int): Player's cumulative playtime on the map
        points (int): Points awarded to the player who completed this race, in thousands
        rank (int): The place that the racetime took on the map toplist
        created (datetime): Datetime when the record was made
        last_played (datetime): Datetime when the playtime stats were updated
    """
    player = models.ForeignKey(Player)
    map = models.ForeignKey(Map)
    server = models.ForeignKey(Server, on_delete=models.SET_NULL, **_null)
    time = models.IntegerField(**_null)
    playtime = models.BigIntegerField(default=0)
    points = models.IntegerField(default=0)
    rank = models.IntegerField(default=0)
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
        time (int): Time to complete the race in milliseconds (null if no time was made)
        playtime (int): Player's cumulative playtime on the map
        points (int): Points awarded to the player who completed this race, in thousands, used to compute player
                      'skill'. -1000 means not yet evaluated.
        rank (int): The place that the racetime took on the map toplist, used to display gold/silver/bronze medals.
                    Updated during point calculation.
        created (datetime): Datetime when the record was made
        last_played (datetime): Datetime when the playtime stats were updated
    """
    player = models.ForeignKey(Player)
    map = models.ForeignKey(Map)
    server = models.ForeignKey(Server, on_delete=models.SET_NULL, **_null)
    time = models.IntegerField(**_null)
    playtime = models.BigIntegerField(default=0)
    points = models.IntegerField(default=0)
    rank = models.IntegerField(default=0)
    created = models.DateTimeField(default=timezone.now)
    last_played = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('player', 'map')

    def __unicode__(self):
        return 'player: {}, map: {}, time: {}'.format(self.player.simplified,
                                                      self.map.name, self.time)

    def time_formatted(self):
        return millis_to_str(int(self.time))

    def playtime_formatted(self):
        # return datetime.timedelta(milliseconds=int(self.playtime))
        return millis_to_str(int(self.playtime))

    def get_points(self):
        # transform points back to float with 3 decimals
        return float(self.points / 1000.0)

    def set_points(self, points):
        # keeps 3 decimals by multiplying with 1000
        self.points = int(points * 1000)

    def get_date(self):
        return self.created.strftime("%Y-%m-%d %H:%M:%S")


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
