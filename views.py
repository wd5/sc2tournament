from django.http import HttpResponse, Http404
from django.template import Template, Context, RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from sc2tournament.models import Player, Tournament, Team
from sc2tournament.forms import TournamentForm, TeamForm
from django.utils import simplejson
from django.db.models import Q
from django.contrib.auth.decorators import login_required, permission_required
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
def tournament_info(request, id):
    """
    Get the json for any tournament based on its id
    """
    t = get_object_or_404(Tournament, id=int(id))
    tournament = t.as_dictionary()
    return JsonResponse(tournament)

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
def tournament_create(request):
    """
    This function is called when we want to create a tournament via form
    """
    if request.method == "POST":
        tournament_form = TournamentForm(request.POST)

        if tournament_form.is_valid():
            p = request.user.get_profile()
            t = tournament_form.save(commit=False)
            t.organized_by = p
            t.save()

    else:
        tournament_form = TournamentForm()

    return render_to_response('create_tournament.html', locals(),
                              context_instance=RequestContext(request))

@login_required
def team_create(request):
    """
    """
    if request.method == "POST":
        team_form = TeamForm(request.POST)
        if team_form.is_valid():
            p = request.user.get_profile()
            t = team_form.save(commit=False)
            t = Team.createTeam(t.name, p, t.size)
    else:
        team_form = TeamForm()

    return render_to_response('create_team.html', locals(),
                              context_instance=RequestContext(request))
            


@login_required
def test_search_page(request):
    sw = Player.objects.get(name='SweetWheat', character_code=601)

    values = {
        'title' : u'Sample Page',
        'badge_test' : sw,
    }

    return render_to_response('test.html', values,
                              context_instance=RequestContext(request))

@login_required
def test_tournament_page(request, tournament_id):
    values = {
        'tournament_id' : tournament_id,
    }
    t = get_object_or_404(Tournament, tournament_id)
    if t.status == u'org':
        raise Http404

    return render_to_response('test_tree.html', values,
                              context_instance=RequestContext(request))
