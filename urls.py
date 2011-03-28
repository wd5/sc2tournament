from django.conf.urls.defaults import *
from sc2tournament.models import Player

urlpatterns = patterns('sc2tournament.views',
    (r'^player/list/$', 'list_players'),
    (r'^player/search/$', 'search'),
)
