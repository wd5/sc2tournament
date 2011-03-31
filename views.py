from django.http import HttpResponse
from django.template import Template, Context, RequestContext
from django.shortcuts import render_to_response
from sc2tournament.models import Player
from django.utils import simplejson
from django.db.models import Q

class JsonResponse(HttpResponse):
    """ A potentially useful class I found on stackoverflow that would allow
        us to return json little bit more easier """

    def __init__(self, data):
        content = simplejson.dumps(data, indent=2, ensure_ascii=False)
        super(JsonResponse, self).\
             __init__(content, mimetype='application/json; charset=utf8')

def list_players(request, list_of_players=Player.objects.all()):
    players = {}
    players['players'] = []
    players['total'] = len(list_of_players)

    # Making a non django-orm model of the data for client
    for p in list_of_players: 
        players['players'].append({
            u'name'              : p.name, 
            u'character_code'    : p.character_code, 
            u'region'            : p.region,
            u'battlenet_id'      : p.battlenet_id,
            u'achievement_points': p.achievement_points,
            u'last_sync'         : p.last_sync.strftime('%Y-%m-%dT%H:%M:%S'),
            u'portrait_iconset'  : p.port_iconset,
            u'portrait_row'      : p.port_row,
            u'portrait_column'   : p.port_column,
        })
    return JsonResponse(players)

def search(request):
    query = request.GET.get('query', '')

    if query:
        qset = (
            Q(name__icontains=query) |
            Q(character_code__icontains=query)
        )
        results = Player.objects.filter(qset).distinct()
    else:
        results = []
    return list_players(request, results)

def test_search_page(request):
    #SweetWheat is always the first player in our test code
    sw = Player.objects.all()[0]
    values = {
        'title' : u'Sample Page',
        'badge_test' : sw,
    }
    return render_to_response('test.html',
                              values,
                              context_instance=RequestContext(request))
