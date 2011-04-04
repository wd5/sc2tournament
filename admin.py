from django.contrib import admin
from sc2tournament.models import Player, Team, Membership, Tournament


class PlayerAdmin(admin.ModelAdmin):
    """ Simple admin model to show just relevant fields if they choose to add a user via admin interface... """
    """ Not too fancy.... """
    #fieldsets = ((None, {'fields' : ('achievement_points', 'battlenet_id')}))
    fields = ('name', 'character_code', 'region', 'user')


class TeamAdmin(admin.ModelAdmin):
    """ Simple admin model to organize teams little bit more clearly """
    class Meta:
        ordering = ['-player', '-team']


admin.site.register(Team)
admin.site.register(Membership)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Tournament)

