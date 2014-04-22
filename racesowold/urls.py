from django.conf.urls import patterns
from . import views

urlpatterns = patterns(
    '',
    (r'^race', views.APIRace.as_view())
)
