from django.conf.urls.defaults import *

urlpatterns = patterns('sc2tournament.views',
    #---Debug Views---#
    (r'^player/list/$', 'player_list'), #debug function
    (r'^team/list/$', 'team_list'), #debug function
    (r'^tournament/list/$', 'tournament_list'), #debug function
    #---JSON API Functions---#
    (r'^player/search/$', 'player_search'),
    (r'^team/search/$', 'team_search'),
    (r'^tournament/search/$', 'tournament_search'),
    (r'^tournament/info/(?P<tournament_id>\d+)/$', 'tournament_info'),
    #---Form related functions---#
    (r'^tournament/join/$', 'tournament_join'),
    (r'^tournament/accept/$', 'tournament_accept'),
    (r'^tournament/reject/$', 'tournament_reject'),
    (r'^tournament/start/$', 'tournament_start'),
    #---Page Related Functions---#
    (r'^tournament/create/$','tournament_create'),
    (r'^team/create/$', 'team_create'),
    (r'^team/status/$', 'team_status'),
    (r'^tournament/status/$', 'tournament_status'),
    (r'^overview/$', 'overview'),
)
