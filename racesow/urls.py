from django.conf.urls import patterns
from . import views

urlpatterns = patterns(
    '',
    (r'^api/map/$', views.APIMapList.as_view()),
    (r'^api/map/([A-Za-z0-9-_=]+)', views.APIMap.as_view()),
    (r'^api/player/([A-Za-z0-9-_=]+)', views.APIPlayer.as_view()),
    (r'^api/nick/([A-Za-z0-9-_=]+)', views.APINick.as_view()),
    (r'^api/race', views.APIRace.as_view())
)
