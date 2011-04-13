from django import forms
from sc2tournament.models import Player, Tournament, Team
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import email_re

#taken from https://gist.github.com/771052
class UniqueEmailField(forms.EmailField):
    """
    Extend EmailField to require uniqueness, we will use this instead of
    username.
    """
    def validate(self, value):
        super(UniqueEmailField, self).valdidate(value)
        try:
            User.objects.get(email = value)
            raise ValidationError('User\'s email already exists.')
        except User.MultipleObjectsReturned:
            raise ValidationError('User\'s email already exists.')
        except User.DoesNotExist:
            #this is what we want to see..
            pass
            

class PlayerForm(forms.ModelForm):
    """
    Simple ModelForm that only shows the data we would expect a user to be able
    to enter.
    """
    class Meta:
        model  = Player
        fields = ('name', 'character_code', 'region')

class TeamForm(forms.ModelForm):
    """
    """
    class Meta:
        model = Team
        fields = ('name', 'region', 'size')

class TournamentForm(forms.ModelForm):
    """
    Simple ModelForm to create new Tournaments
    """
    class Meta:
        model = Tournament
        fields = ('name', 'size', 'best_of', 'region')

class UserWithNameForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        """
        Need to rename the username field, we are going to only
        use email addys
        """
        super(UserWithNameForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = 'Account/E-Mail'

    def save(self, *args, **kwargs):
        """
        Copies username into email
        """
        self.instance.email = self.instance.username
        u = super(UserWithNameForm, self).save(*args, **kwargs)
        return u
