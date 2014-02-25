from django.contrib import admin
from .models import Tag, Server, Map, MapRating, PlayerHistory
from .models import Player, RaceHistory, Race, Checkpoint

admin.site.register(Tag)
admin.site.register(Server)
admin.site.register(Map)
admin.site.register(MapRating)
admin.site.register(PlayerHistory)
admin.site.register(Player)
admin.site.register(RaceHistory)
admin.site.register(Race)
admin.site.register(Checkpoint)