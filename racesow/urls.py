from django.conf.urls import patterns, url, include
from rest_framework import routers

from racesow.views.default import NotFound

import racesow.views.api as api
import racesow.views.drf as drf
import racesow.views.site as website
import racesow.views.wmm as wmm

router = routers.DefaultRouter()
router.register(r'players', drf.PlayerViewSet)
router.register(r'maps', drf.MapViewSet)
router.register(r'tags', drf.TagViewSet)
router.register(r'races', drf.RaceViewSet)
router.register(r'checkpoints', drf.CheckpointViewSet)
router.register(r'races-1.0', drf.Race10ViewSet)

urlpatterns = patterns(
    '',
    url(r'^$', website.Index.as_view(), name='home'),

    url(r'^timezone$', website.SetTimezone.as_view(), name='tz'),
    url(r'^preferences$', website.Preferences.as_view(), name='prefs'),

    # details of a single player (pdn = Player Details New, pdn = Player Details Old)
    url(r'^players/detail/(?P<playerid>\d+)[/]*$', website.PlayerDetails.as_view(), {'version': 'new'}, name='pdn'),
    url(r'^players/detail/(?P<playerid>\d+)/(?P<order>[-\w]+)/(?P<page>\d+)$', website.PlayerDetails.as_view(), {'version': 'new'}, name='pdn2'),
    url(r'^players/detail/(?P<playerid>\d+)/(?P<order>[-\w]+)/(?P<page>\d+)/(?P<q>[-\w]*)$', website.PlayerDetails.as_view(), {'version': 'new'}, name='pdn3'),

    url(r'^players-old/detail/(?P<playerid>\d+)[/]*$', website.PlayerDetails.as_view(), {'version': 'old'}, name='pdo'),
    url(r'^players-old/detail/(?P<playerid>\d+)/(?P<order>[-\w]+)/(?P<page>\d+)$', website.PlayerDetails.as_view(), {'version': 'old'}, name='pdo2'),
    url(r'^players-old/detail/(?P<playerid>\d+)/(?P<order>[-\w]+)/(?P<page>\d+)/(?P<q>[-\w]*)$', website.PlayerDetails.as_view(), {'version': 'old'}, name='pdo3'),

    # list of players (pln = Player List New, plo = Player List Old)
    url(r'^players/$', website.PlayerList.as_view(), {'version': 'new'}, name="pln"),
    url(r'^players/(?P<order>[-\w]+)/(?P<page>\d+)$', website.PlayerList.as_view(), {'version': 'new'}, name="pln2"),
    url(r'^players/(?P<order>[-\w]+)/(?P<page>\d+)/(?P<q>[-\w]*)$', website.PlayerList.as_view(), {'version': 'new'}, name="pln3"),

    url(r'^players-old/$', website.PlayerList.as_view(), {'version': 'old'}, name="plo"),
    url(r'^players-old/(?P<order>[-\w]+)/(?P<page>\d+)$', website.PlayerList.as_view(), {'version': 'old'}, name="plo2"),
    url(r'^players-old/(?P<order>[-\w]+)/(?P<page>\d+)/(?P<q>[-\w]*)$', website.PlayerList.as_view(), {'version': 'old'}, name="plo3"),

    # details of a single map (mdn = Map Details New, mdo = Map Details Old)
    url(r'^maps/detail/(?P<mapid>\d+)[/]*$', website.MapDetails.as_view(), {'version': 'new'}, name='mdn'),
    url(r'^maps/detail/(?P<mapid>\d+)/(?P<order>[-\w]+)/(?P<page>\d+)$', website.MapDetails.as_view(), {'version': 'new'}, name='mdn2'),

    url(r'^maps-old/detail/(?P<mapid>\d+)[/]*$', website.MapDetails.as_view(), {'version': 'old'}, name='mdo'),
    url(r'^maps-old/detail/(?P<mapid>\d+)/(?P<order>[-\w]+)/(?P<page>\d+)$', website.MapDetails.as_view(), {'version': 'old'}, name='mdo2'),

    # list of maps (mln = Map List New, mlo = Map List Old)
    url(r'^maps/$', website.MapList.as_view(), {'version': 'new'}, name='mln'),
    url(r'^maps/(?P<order>[-\w]+)/(?P<page>\d+)$', website.MapList.as_view(), {'version': 'new'}, name='mln2'),
    url(r'^maps/(?P<order>[-\w]+)/(?P<page>\d+)/(?P<q>[-\w]*)$', website.MapList.as_view(), {'version': 'new'}, name='mln3'),

    url(r'^maps-old/$', website.MapList.as_view(), {'version': 'old'}, name='mlo'),
    url(r'^maps-old/(?P<order>[-\w]+)/(?P<page>\d+)$', website.MapList.as_view(), {'version': 'old'}, name='mlo2'),
    url(r'^maps-old/(?P<order>[-\w]+)/(?P<page>\d+)/(?P<q>[-\w]*)$', website.MapList.as_view(), {'version': 'old'}, name='mlo3'),

    # matchmaking stats of a single player
    url(r'^wmm/(?P<username>.+)$', wmm.MatchMaker.as_view()),

    # Temporary place for restframework api
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    (r'.+', NotFound.as_view()),
)
