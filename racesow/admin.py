from django.contrib import admin
from racesow import models
from simple_history.admin import SimpleHistoryAdmin

admin.site.register(models.Tag)
admin.site.register(models.Server)


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

admin.site.register(models.Map, MapAdmin)
admin.site.register(models.MapRating)
admin.site.register(models.PlayerHistory)
admin.site.register(models.Player, SimpleHistoryAdmin)
admin.site.register(models.RaceHistory)
admin.site.register(models.Race, SimpleHistoryAdmin)
admin.site.register(models.Checkpoint)
