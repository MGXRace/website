import datetime

from django.db import models

from racesow.utils import username_with_html_colors, millis_to_str, weaponstring


_null = {'blank': True, 'null': True, 'default': None}


class Player(models.Model):
    """Racesow Old Player Model

    Model Fields:
        name (str): name with colorcodes
        simplified (str): name without colorcodes
        auth_name (str): login name
        auth_token (str): unused
        auth_email (str): email address
        auth_mask (str): permissions mask
        auth_pass (str): password hash
        session_token (str): unused
        points (int): points the player has
        races (int): number of races the player has finished
        maps (int): number of maps the player has completed a race on
        diff_points (int): change in points over some timeperiod
        awardval (int): Awards given to the playe
        playtime (int): player's ingame playtime in seconds
    """
    name = models.CharField(max_length=64)
    simplified = models.CharField(max_length=64)
    auth_name = models.CharField(max_length=64, blank=True)
    auth_token = models.CharField(max_length=64, blank=True)
    auth_email = models.CharField(max_length=64, blank=True)
    auth_mask = models.CharField(max_length=64, blank=True)
    auth_pass = models.CharField(max_length=64, blank=True)
    session_token = models.CharField(max_length=64, blank=True)
    points = models.IntegerField(default=0)
    races = models.IntegerField(default=0)
    maps = models.IntegerField(default=0)
    diff_points = models.IntegerField(default=0)
    awardval = models.IntegerField(default=0)
    playtime = models.BigIntegerField(default=0)

    def __unicode__(self):
        return '<Player name:{}>'.format(self.simplified)

    def htmlname(self):
        return username_with_html_colors(u'{}'.format(self.name))

    def playtime_formatted(self):
        return millis_to_str(int(self.playtime))


class Map(models.Model):
    """Racesow Old Map Model

    Model Fields:
        name (str): name of the map
        longname (str): longname of the map
        file (str): url to pk3file for the map
        oneliner (str): oneliner message for the record
        pj_oneliner (str): pj_oneliner message for the record
        mapper (Player): mapper
        freestyle (bool): freestyle
        status (str): status
        races (int): number of completed races
        playtime (int): playtime on the map in seconds
        rating (float): average rating of the map
        ratings (int): number of ratings for the map
        downloads (int): number of times the pk3 was downloaded
        force_recompution (str): recompute points for the map
        weapons (str): bitmask string (wtf?) identifing weapons on the map
        created (datetime): Datetime map was added
    """
    name = models.CharField(max_length=255)
    longname = models.CharField(max_length=255, **_null)
    file = models.CharField(max_length=255, **_null)
    oneliner = models.CharField(max_length=255, **_null)
    pj_oneliner = models.CharField(max_length=255, **_null)
    mapper = models.ForeignKey(Player, **_null)
    freestyle = models.BooleanField(default=False)
    status = models.CharField(max_length=255)
    races = models.IntegerField(default=0)
    playtime = models.BigIntegerField(default=0)
    rating = models.FloatField(**_null)
    ratings = models.IntegerField(default=0)
    downloads = models.IntegerField(default=0)
    force_recompution = models.CharField(max_length=255)
    weapons = models.CharField(max_length=255)
    created = models.DateTimeField(**_null)

    def __unicode__(self):
        return self.name

    def playtime_formatted(self):
        return datetime.timedelta(seconds=int(self.playtime)/1000)

    def htmlname(self):
        if self.longname:
            return username_with_html_colors(u'{}'.format(self.longname))
        return u''

    def htmlname_short(self, maxlen=32):
        if self.longname:
            return username_with_html_colors(u'{}'.format(self.longname)[:maxlen])
        return u''

    def get_weapons(self):
        return weaponstring('{}'.format(self.weapons))


class Gameserver(models.Model):
    """Racesow Old Server Model

    Model Fields:
        user (str): mysql user for the server
        servername (str): name of the server with colorcodes
        admin (str): username of the admin running the server
        playtime (int): Time played on server in (milli?)seconds
        races (int): Number of races finished on the server
        maps (int): number of maps played on the server
        created (datetime): Date/time the server was created
    """
    user = models.CharField(max_length=64)
    servername = models.CharField(max_length=255)
    admin = models.CharField(max_length=255)
    playtime = models.BigIntegerField(default=0)
    races = models.PositiveIntegerField(default=0)
    maps = models.IntegerField(default=0)
    created = models.DateTimeField(**_null)

    def __unicode__(self):
        return self.simplified


class Checkpoint(models.Model):
    """Racesow Old Checkpoint Model

    Contains the checkpoints for a players race entry

    Model Fields:
        player (Player): player who recorded the checkpoint
        map (Map): map checkpoint was recorded on
        num (int): number of the checkpoint
        time (int): Time of the race that the checkpoint was touched
    """
    player = models.ForeignKey(Player, **_null)
    map = models.ForeignKey(Map, **_null)
    num = models.IntegerField()
    time = models.IntegerField()

    def __unicode__(self):
        return '<Checkpoint(id: {})>'.format(self.id)


class PlayerMap(models.Model):
    """Racesow Old PlayerMap Model

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
    player = models.ForeignKey(Player, **_null)
    map = models.ForeignKey(Map, **_null)
    server = models.ForeignKey(Gameserver, on_delete=models.SET_NULL, **_null)
    time = models.IntegerField(**_null)
    races = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    playtime = models.BigIntegerField(default=0)
    tries = models.IntegerField(default=0)
    duration = models.BigIntegerField(default=0)
    overall_tries = models.IntegerField(default=0)
    racing_time = models.BigIntegerField(default=0)
    created = models.DateTimeField(**_null)
    prejumped = models.CharField(max_length=64)

    def __unicode__(self):
        return 'player: {}, map: {}, time: {}'.format(self.player.simplified,
                                                      self.map.name, self.time)

    def time_formatted(self):
        return millis_to_str(int(self.time))

    def playtime_formatted(self):
        # return datetime.timedelta(milliseconds=int(self.playtime))
        return millis_to_str(int(self.playtime))

    def get_points(self):
        return self.points

    def get_date(self):
        return self.created.strftime("%Y-%m-%d %H:%M:%S")