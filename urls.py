from django.conf.urls.defaults import *

urlpatterns = patterns('sc2tournament.views',
    #---JSON API Functions---#
    (r'^player/list/$', 'player_list'),
    (r'^player/search/$', 'player_search'),
    (r'^team/list/$', 'team_list'),
    (r'^team/search/$', 'team_search'),
    (r'^tournament/list/$', 'tournament_list'),
    (r'^tournament/search/$', 'tournament_search'),
    #---Page Related Functions---#
    (r'tournament/create/$','tournament_create'),
    (r'^team/create/$', 'team_create'),
    #---Site Management Related---#
)
