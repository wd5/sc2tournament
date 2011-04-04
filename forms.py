from django.forms import ModelForm, Form
from sc2tournament.models import Player, Tournament, Team

class PlayerForm(ModelForm):
    """
    Simple ModelForm that only shows the data we would expect a user to be able
    to enter.
    """
    class Meta:
        model  = Player
        fields = ('name', 'character_code', 'region')
