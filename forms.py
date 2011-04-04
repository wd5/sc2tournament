from django import forms
from sc2tournament.models import Player, Tournament, Team

class PlayerForm(forms.ModelForm):
    """
    Simple ModelForm that only shows the data we would expect a user to be able
    to enter.
    """
    class Meta:
        model  = Player
        fields = ('name', 'character_code', 'region')

class TournamentForm(forms.ModelForm):
    """
    Simple ModelForm to create new Tournaments
    """
    #eventually we will add optional passwords to tournaments.. but not now..
    #password1 = forms.CharField(help_text="Password", max_length=20, widget=forms.PasswordInput)
    #password2 = forms.CharField(help_text="Re-enter password", max_length=20, widget=forms.PasswordInput)


    class Meta:
        model = Tournament
        fields = ('name', 'best_of')
