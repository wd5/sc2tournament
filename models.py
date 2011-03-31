from django.db import models
from django.contrib.auth.models import User


REGIONS = [
    (u'us', u'United States'),
    (u'eu', u'Europe'),
    (u'kr', u'South Korea'),
    (u'tw', u'Taiwan'),
    (u'sea',u'Southeast Asia'),
    (u'ru', u'Russia'),
    (u'la', u'Latin America')
]



MEMBERSHIP_STATUS = [
    (u'def', u'Default'),
    (u'pen', u'Pending Approval'),
    (u'app', u'Approved'),
    (u'ban', u'Banned From Team')
]


TOURNAMENT_STATUS = [
    (u'org', u'Being organized'),
    (u'eli', u'Elimination rounds'),
    (u'pro', u'Regular brackets... in progress'),
    (u'com', u'Completed')
]

class Player(models.Model):
    """ Only name and character_code is required. battlenet_id will be populated later """
    auth_account = models.ForeignKey(User, help_text='The django auth model used'
                                     'for storing email & password information...')

    name = models.CharField(max_length=40, help_text='The in game name of the player')
    character_code = models.IntegerField(null=False, help_text='The 3 - 5 digit code representing a players code')
    battlenet_id = models.IntegerField(blank=True, default=0)
    region = models.CharField(max_length=4, choices=REGIONS, help_text='The region of this battle net account')
    achievement_points = models.IntegerField(blank=True, default=0)

    # Information related to last sync and sc2rank's age of the information replicated
    sc2ranks_last_updated = models.DateTimeField(blank=True, auto_now_add=True)    #the time sc2ranks was updated different than our sync time
    last_sync = models.DateTimeField(blank=True, null=True, auto_now_add=True) 
    join_date = models.DateTimeField(auto_now_add=True)

    #portrait information - maybe make seperate table to normalize(?)
    port_iconset = models.IntegerField(null=False, default=0)
    port_row     = models.IntegerField(null=False, default=0)
    port_column  = models.IntegerField(null=False, default=0)

    @staticmethod
    def createPlayer(name, code, region, account):
        """ Static method shorthand for creating a player """
        return Player(name=name, character_code=code, region=region, auth_account=account)

    def generate_badge_html(self):
        """ This function generates a div containing displayable HTML for a badge """
        """ Not sure if there is a more logical place to put this code, maybe in  """
        """ the view or another utility type file. """
        return u''
    def __unicode__(self):
        return u'%s <%d> %s' % (self.name, self.character_code, self.region)

class Team(models.Model):
    """ A team is a collection of Players; organized by a specific player, that can participate in tournaments. """
    leader = models.ForeignKey(Player, help_text='The player that organized this team', related_name='+')
    name = models.CharField(max_length = 80, blank=True)
    members = models.ManyToManyField(Player, through='Membership')
    date_formed = models.DateField(auto_now_add=True)

    @staticmethod
    def createTeam(name, leader):
        """ Static method shorthand for creating a team """
        return Team(name=name, leader=leader)

    def __unicode__(self):
        if not self.name:
            return u'no name'
        return u'%s' % (self.name)


class Membership(models.Model):
    """ Manages the teams - relation between players and teams """
    team = models.ForeignKey(Team)
    player = models.ForeignKey(Player)

    date_player_joined = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=3, choices=MEMBERSHIP_STATUS, default=MEMBERSHIP_STATUS[0][0]) #default status is def

    @staticmethod
    def createMembership(player, team):
        """ Simple method shorthand for creating team """
        return Membership(team=team, player=player)

    def __unicode__(self):
        return u'%s (%s)' % (self.player, self.team)

class Tournament(models.Model):
    """ Manages the tounraments - a grouping of teams competing at a given date and time """
    name = models.CharField(max_length=80, blank=False, help_text='The visible name of the tournament')
    competing_teams = models.ManyToManyField(Team)

    time_created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=4, choices=TOURNAMENT_STATUS, help_text='Current status of this tournament')
