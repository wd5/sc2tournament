from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import Template, Context, RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from sc2tournament.models import Player, Tournament, Team
from sc2tournament.forms import TournamentForm, TeamForm
from django.utils import simplejson
from django.db.models import Q
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
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
def tournament_info(request, tournament_id):
    """
    Get the json for any tournament based on its id
    """
    t = get_object_or_404(Tournament, id=int(tournament_id))
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
            return HttpResponseRedirect(reverse('sc2tournament.views.tournament_status'))
    else:
        tournament_form = TournamentForm()

    return render_to_response('create_tournament.html', locals(),
                              context_instance=RequestContext(request))


@login_required
def tournament_join(request):
    """
    Join a team into the pending queue of a tournament
    """
    #look at Tournament.add_team_pending
    me = request.user.get_profile()

    return render_to_response('tournament_list.html', locals(),
                              context_instance=RequestContext(request))



@login_required
def tournament_accept(request):
    """
    Move a team from the accepted queue to the reject queue in a tournament
    """
    #look at Tournament.reject_team
    me = request.user.get_profile()

    #make sure they are posting a form.
    if request.method != "POST":
        return HttpResponseRedirect(reverse('sc2tournament.views.tournament_status'))

    #get information from post...
    team = Team.objects.get(pk=request.POST['team_id'])
    tournament = Tournament.objects.get(pk=request.POST['tournament_id'])

    #make sure that the 'me' is the organizer
    if tournament.organized_by != me:
        return HttpResponse("You cannot manage this tournament...")

    #if there is problems with the logic catch exception and show errors
    try:
        tournament.accept_team(team)
    except Exception as e:
        return HttpResponse(e)

    return HttpResponseRedirect(reverse('sc2tournament.views.test_tournament_page',
                                kwargs={ 'tournament_id' : tournament.id }))

@login_required
def tournament_reject(request):
    """
    Move a team from the accepted queue to the reject queue in a tournament
    """
    #look at Tournament.reject_team
    me = request.user.get_profile()

    #make sure they are posting a form.
    if request.method != "POST":
        return HttpResponseRedirect(reverse('sc2tournament.views.tournament_status'))

    #get information from post...
    team = Team.objects.get(pk=request.POST['team_id'])
    tournament = Tournament.objects.get(pk=request.POST['tournament_id'])

    #make sure that the 'me' is the organizer
    if tournament.organized_by != me:
        return HttpResponse("You cannot manage this tournament...")

    #if the tournament is in progress, remove this option
    if tournament.status != u'org':
        return HttpResponse("You cannot remove a team once the tournament has started")

    #if there is problems with the logic catch exception and show errors
    try:
        tournament.reject_team(team)
    except Exception as e:
        return HttpResponse(e)

    return HttpResponseRedirect(reverse('sc2tournament.views.test_tournament_page',
                                kwargs={ 'tournament_id' : tournament.id }))

@login_required
def tournament_start(request):
    """
    When an organizer of a tournament wants to start the event
    """
    a = u'%s %s' % (request.POST['value'], request.POST['tournament_id'])
    t = get_object_or_404(Tournament, id=request.POST['tournament_id'])
    try:
        t.start_tournament()
    except Exception as e:
        return HttpResponse(e)

    return HttpResponseRedirect(reverse('sc2tournament.views.test_tournament_page',
                                kwargs={ 'tournament_id' : t.id }))

@login_required
def team_status(request):
    """
    Overview page for teams - create, accept, reject, list
    """
    #their sc2 player
    me = request.user.get_profile()

    #teams they can manage
    my_teams = Team.objects.filter(leader=me)

    #organizing teams they are part of
    my_pending_teams = Team.objects.filter(members=me, status=u'org')

    #active teams they are apart of
    my_active_teams = Team.objects.filter(members=me, status=u'act')

    return render_to_response('team_list.html', locals(),
                              context_instance=RequestContext(request))
@login_required
def tournament_status(request):
    #get the user's sc2 player account
    me = request.user.get_profile()

    #get the tournaments they made
    my_tournaments = Tournament.objects.filter(organized_by=me)
    
    #only show the tournaments that they have potential to be in
    my_pending_tournaments = Tournament.objects\
                             .filter(pending_teams=me.my_teams.all(),
                                     status=u'org')

    #show the tournaments they are in they aren't over
    my_current_tournaments = Tournament.objects\
                             .filter(competing_teams=me.my_teams.all())\
                             .exclude(status=u'com')

    #show the tournaments they are in that ARE over
    my_previous_tournaments = Tournament.objects\
                              .filter(competing_teams=me.my_teams.all(),
                                      status=u'com')

    #render all this shit on the page! :P
    return render_to_response('tournament_list.html', locals(),
                              context_instance=RequestContext(request))

@login_required
def team_create(request):
    """
    Creates a team with form
    """
    if request.method == "POST":
        team_form = TeamForm(request.POST)
        if team_form.is_valid():
            p = request.user.get_profile()
            t = team_form.save(commit=False)
            t = Team.createTeam(t.name, p, t.size)

            #redirect them back to tournaments page..
            return HttpResponseRedirect(reverse('sc2tournament.views.tournament_status'))
    else:
        team_form = TeamForm()

    return render_to_response('create_team.html', locals(),
                              context_instance=RequestContext(request))
            

@login_required
def overview(request):
    return render_to_response('overview.html', locals(),
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
    t = get_object_or_404(Tournament, id=tournament_id)

    return render_to_response('test_tree.html', locals(),
                              context_instance=RequestContext(request))
