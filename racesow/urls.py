from django.conf.urls import patterns, url

from racesow.views.default import NotFound

import racesow.views.api as api
import racesow.views.site as website
import racesow.views.wmm as wmm

urlpatterns = patterns(
    '',
    url(r'^$', website.Index.as_view(), name='home'),

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

    # api calls for server
    (r'^api/map/$', api.APIMapList.as_view()),
    (r'^api/map/([A-Za-z0-9-_=]+)', api.APIMap.as_view()),
    (r'^api/player/([A-Za-z0-9-_=]+)', api.APIPlayer.as_view()),
    (r'^api/nick/([A-Za-z0-9-_=]+)', api.APINick.as_view()),
    (r'^api/race[/]*$', api.APIRace.as_view()),
    (r'^api/raceall$', api.APIRaceAll.as_view()),
    (r'.+', NotFound.as_view()),
)
