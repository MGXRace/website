from django.contrib import admin
from .models import Gameserver, Map, Player, PlayerMap, Checkpoint

admin.site.register(Gameserver)
admin.site.register(Map)
admin.site.register(Player)
admin.site.register(PlayerMap)
admin.site.register(Checkpoint)
