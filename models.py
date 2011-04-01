from django.db import models
from django.contrib.auth.models import User
from math import log
from operator import mod

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

SET_TYPES = (
    (u'eli', u'Elimination Round'),
    (u'reg', u'Regular RO type set')
)

SET_STATUS = [
    (u'not', u'Not started yet'),
    (u'pro', u'Match is in progress'),
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
    status = models.CharField(max_length=4, choices=TOURNAMENT_STATUS,
                              default=TOURNAMENT_STATUS[0][0],
                              help_text='Current status of this tournament')
    best_of = models.IntegerField(default=3, help_text='Matches required before its considered won')

    def __unicode__(self):
        if not self.name:
            return u'Unnamed Tournament (%s)' % (self.competing_teams.all())
        return u'%s (%s)' % (self.name, self.competing_teams.all())

    def start_tournament(self):
        """ Starts a tournament. """
        """ Sets the status appropriately, and creates all the sets for the tournament as """
        """ well as the elimination rounds if necessary """

        #we only can start a tournament if we have a base 2 amount of players
        #later we will add elimination rounds to help deal with realistic conditions
        if mod(log(self.competing_teams.count(), 2), 1) != 0:
            raise ValueError('There wasn\'t enough teams in tournament %s to start.  '
                             'Only %d teams.' % (self.name, set_counter))

        set_counter = self.competing_teams.count() - 1
        self.status = TOURNAMENT_STATUS[2][0]
        
        while set_counter > 0:
            #assume that there are a log2 based amount of teams... no elmination rounds yet.
            s = Set()
            s.in_tournament = self
            s.set_number = set_counter
            set_counter -= 1
            s.save()

        set_counter = self.competing_teams.count() - 1 
        for t in self.competing_teams.all():
            #add a team in the competing teams to the set, filling backwards.
            #picture the matches as a perfect binary tree, 1 being root and counting
            #left to right down the tree.
            s = self.all_sets_in_tournament.get(set_number=set_counter)
            
            #set this match to being in progress
            s.set_status = SET_STATUS[1][0]

            s.competing_teams.add(t)
            if s.competing_teams.count() == 2:
                #if we added two teams to the set. decrease our set_counter
                set_counter -= 1

            #make sure the set saves the status change
            s.save()


class Set(models.Model):
    """ Sets exist four tournaments. Need to keep track of the which when matches are completed """
    """ Each match can have as many teams as it wants to... but UI will support ONLY 2 """ 
    in_tournament = models.ForeignKey(Tournament, related_name='all_sets_in_tournament', 
                                      help_text='From this tournament')
    set_type = models.CharField(max_length=3, choices=SET_TYPES, default=SET_TYPES[1][0],
                                help_text='A status tracker for when we eventually do elmination rounds')
    set_status = models.CharField(max_length=3,  choices=SET_STATUS, default=SET_STATUS[0][0],
                                  help_text='Has it started? Is it over? Is it a placeholder?')
    winner = models.ForeignKey(Team, null=True, blank=True, related_name='+',
                               help_text='The team that one this set')
    set_number = models.IntegerField(help_text='Used to represent the tournament tree aka brackets')
    competing_teams = models.ManyToManyField(Team, related_name='all_set_history', 
                                             help_text='All the teams in this match.. should be 2...')

class Match(models.Model):
    """ Each match is part of a set and represents a game """
    """ Maybe we can add replay file uploads and stuff later here if interested """
    """ For now this will be a dumb class, just used for select count(*) type things """
    """ so it doesn't matter which match is added or removed """
    in_set = models.ForeignKey(Set, related_name='matches', 
                               help_text='The set this was from')
    winner = models.ForeignKey(Team, null=True, blank=True, help_text='The team that one this match')
