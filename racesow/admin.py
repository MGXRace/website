from django.contrib import admin
from .models import Tag, Server, Map, MapRating, PlayerHistory
from .models import Player, RaceHistory, Race, Checkpoint

admin.site.register(Tag)
admin.site.register(Server)


class MapAdmin(admin.ModelAdmin):
    list_display = ('name', 'enabled', 'get_tags')
    ordering = ('name', )
    search_fields = ('name', )
    # specify fields to show on the add-page
    fieldsets = (
        (None, {
            'fields': ('name', 'pk3file', 'tags'),
            'classes': ('wide', ),
        }),
    )

    # add extra css definitions for the add-page
    class Media:
        css = {
            'all': ('admin/css/admin_extra.css',)
        }

admin.site.register(Map, MapAdmin)
admin.site.register(MapRating)
admin.site.register(PlayerHistory)
admin.site.register(Player)
admin.site.register(RaceHistory)
admin.site.register(Race)
admin.site.register(Checkpoint)
