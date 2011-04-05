from django.http import HttpResponse
from django.template import Template, Context, RequestContext
from django.shortcuts import render_to_response
from sc2tournament.models import Player, Tournament, Team
from django.utils import simplejson
from django.db.models import Q
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
import logging

logger = logging.getLogger(__name__)

class JsonResponse(HttpResponse):
    """ A potentially useful class I found on stackoverflow that would allow
        us to return json little bit more easier """

    def __init__(self, data):
        content = simplejson.dumps(data, indent=2, ensure_ascii=False)
        super(JsonResponse, self).\
             __init__(content, mimetype='application/json; charset=utf8')

@login_required
def player_list(request, list_of_players=Player.objects.all()):
    players = {}
    players['players'] = []
    players['total'] = len(list_of_players)

    # Making a non django-orm model of the data for client
    for p in list_of_players: 
        players['players'].append(p.as_dictionary())

    return JsonResponse(players)

@login_required
def player_search(request):
    query = request.GET.get('query', '')

    if query:
        qset = (
            Q(name__icontains=query) |
            Q(character_code__icontains=query)
        )
        results = Player.objects.filter(qset).distinct()
    else:
        results = []
    return player_list(request, results)

def team_list(request, list_of_teams=Team.objects.all()):
    teams = {}
    teams['teams'] = []
    teams['total'] = len(list_of_teams)

    for t in list_of_teams:
        teams['teams'].append(t.as_dictionary())

    return JsonResponse(teams)

def team_search(request):
    query = request.GET.get('query', '')
    
    if query:
        qset = ( Q(name__icontains=query) )
        results = Team.objects.filter(qset).distinct()
    else:
        results = []

    return team_list(request, results)

def tournament_list(request, list_of_tournaments=Tournament.objects.all()):
    tournaments = {}
    tournaments['tournaments'] = []
    tournaments['total'] = len(list_of_tournaments)

    for t in list_of_tournaments:
        tournaments['tournaments'].append(t.as_dictionary())

    return JsonResponse(tournaments)

def tournament_search(request):
    query = request.GET.get('query', '')

    if query:
        qset = ( Q(name__icontains=query) )
        results = Tournament.objects.filter(qset).distinct()
    else:
        results = []
    return tournament_list(request, results)

@login_required
def test_search_page(request):
    #SweetWheat is always the first player in our test code
    sw = Player.objects.all()[0]
    values = {
        'title' : u'Sample Page',
        'badge_test' : sw,
    }
    return render_to_response('test.html', values,
                              context_instance=RequestContext(request))

