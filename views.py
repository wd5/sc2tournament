from django.http import HttpResponse
from sc2tournament.models import Player
from django.core import serializers
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

    # Making a non django-orm model of the data for client
    for p in list_of_players: 
        players['players'].append({
            u'name'              : p.name, 
            u'character_code'    : p.character_code, 
            u'region'            : p.region,
            u'battlenet_id'      : p.battlenet_id,
            u'achievement_points' : p.achievement_points,
            u'last_synced'       : p.last_sync.strftime('%Y-%m-%dT%H:%M:%S')
        })
    return JsonResponse(players) 




def search(request):
    query = request.GET.get('q', '')
    if query:
        qset = (
            Q(name__icontains=query) |
            Q(character_code__icontains=query)
        )
        results = Player.objects.filter(qset).distinct()
    else:
        results = []
    return list_players(request, results)
