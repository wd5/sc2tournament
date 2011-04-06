from django.db import models
from django.contrib.auth.models import User
from math import log
from operator import mod
from sc2tournament.managers import SetManager, MembershipManager

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
    (u'pen', u'Pending Approval'),
    (u'app', u'Approved'),
    (u'dec', u'Declined')
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

BEST_OF_CHOICES = [
    (1, u'Single Round'),
    (3, u'Best of 3'),
    (5, u'Best of 5'),
    (7, u'Best of 7'),
]

TEAM_STATUS = [
    (u'org', u'Being organized'),
    (u'act', u'Active'),
    (u'dis', u'Disbanded'),
]

TEAM_SIZES = [
    (1, u'1v1'),
    (2, u'2v2'),
    (3, u'3v3'),
    (4, u'4v4'),
]

class Player(models.Model):
    """ Only name and character_code is required. battlenet_id will be pop- """
    """ ulated later """
    user = models.OneToOneField(User, 
                                help_text='The django auth model used for'
                                'storing email & password information...')

    name = models.CharField("Character name", max_length=40,
                            help_text='The in game name of the player')
    character_code = models.IntegerField(null=False, help_text='The 3-5 digit '
                                         'code representing a players code')
    battlenet_id = models.IntegerField("Battle.net Id", editable=False,
                                       blank=True, default=0)
    region = models.CharField("Geographic Location", max_length=4,
                              choices=REGIONS,
                              help_text='The region of this battle net account')
    achievement_points = models.IntegerField(blank=True, default=0)

    # Information related to last sync and sc2rank's age of the information 
    # replicated
    sc2ranks_last_updated = models.DateTimeField("Age of profile information", 
                                                 editable=False, blank=True, 
                                                 auto_now_add=True)
                                                 
    last_sync = models.DateTimeField(blank=True, null=True, auto_now_add=True) 
    join_date = models.DateTimeField(auto_now_add=True)

    #portrait information - maybe make seperate table to normalize(?)
    port_iconset = models.IntegerField(null=False, default=0)
    port_row     = models.IntegerField(null=False, default=0)
    port_column  = models.IntegerField(null=False, default=0)

    class Meta:
        #Makes a componded key for players. Works with form validation.
        unique_together = (
            ('name','character_code'),
        )
        db_table = 'players'

    @staticmethod
    def createPlayer(name, code, region, account):
        """ Static method shorthand for creating a player """
        return Player(name=name, character_code=code, region=region, 
                      user=account)

    def as_dictionary(self):
        return {
            u'name'              : self.name, 
            u'character_code'    : self.character_code, 
            u'region'            : self.region,
            u'battlenet_id'      : self.battlenet_id,
            u'achievement_points': self.achievement_points,
            u'last_sync'         : self.last_sync.strftime('%Y-%m-%dT%H:%M:%S'),
            u'portrait_iconset'  : self.port_iconset,
            u'portrait_row'      : self.port_row,
            u'portrait_column'   : self.port_column,
        }

    def __unicode__(self):
        return u'%s <%d> %s' % (self.name, self.character_code, self.region)

class Team(models.Model):
    """
    A team is a collection of Players; organized by a specific player that can
    participate in tournaments when they are filled/completed.

    Once a team is created/filled it should impossible to break the team up
    to avoid confusion of who played which games.  Multiple teams, plus making
    teams "inactive" status would make more sense.
    """
    leader = models.ForeignKey(Player, help_text='The player that organized'
                               'this team', related_name='+')
    name = models.CharField(max_length=80, blank=True)
    members = models.ManyToManyField(Player, through='Membership')
    date_formed = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=3, choices=TEAM_STATUS,
                              default=TEAM_STATUS[0][0],
                              help_text='Fast status to readiness of team.')
    size = models.IntegerField(default=1, choices=TEAM_SIZES,
                               help_text='The number of players requried to '
                               'complete this team.')

    class Meta:
        unique_together = (
            ('leader', 'name'),
        )
        db_table = 'teams'

    @staticmethod
    def createTeam(name, leader, size):
        """ Static method shorthand for creating a team """

        if size < 1 or size > 4:
            raise ValueError('Can only create teams with 1-4 size (players)')

        #create saves it with these values
        t = Team.objects.create(name=name, leader=leader, size=size)

        #the team leader should be a member of the team...
        t.add_player(leader)
        t.accept_player(leader)
        t.save()
        return t

    def as_dictionary(self):
        return {
            u'leader' : self.leader.as_dictionary(),
            u'name'   : self.name,
            u'status' : self.status,
            u'size'   : self.size,
            u'members': [x.as_dictionary() for x in self.members.all()],
        }

    def __unicode__(self):
        if self.name:
            return u'%s#%d-%s' % (self.leader.name, self.leader.character_code,
                                self.name)
        return u'%s-GenericTeam' % (self.leader)

    def add_player(self, player):
        """
        Tries to add a player to the team. This is not the same as when the
        member gets approved from the team leader.
        """
        #if the team not active or disbanded...
        if self.status != u'org':
            raise ValueError('Cannot add \'%s\' to already active/inactive '
                             'team \'%s\'' % (player, self))

        #make sure they aren't already on the team in anyway...
        if player in self.members.all():
            raise ValueError('Cannot add \'%s\' twice to team \'%s\'' %
                            (player, self))
        #we can add them
        m = Membership.objects.create(team=self, player=player)
        return m

    def accept_player(self, player):
        """
        Will accept a pending player on a team to be accepted status.  When
        these events occur the team may changes its own status to active.
        """
        #check to see if the team is still in organizing status
        if self.status != u'org':
            raise ValueError('Cannot add player \'%s\' to team \'%s\' the team'
                             ' is active or disbanded. ' % (player, self))

        #While we debug, this might help catch mistakes in logic
        if Membership.objects.approved(self).count() >= self.size:
            raise ValueError('Somehow team \'%s\' has organizing status and is'
                             ' overly full' % (self))

        #change their status to 'approved' aka 'app'
        m = Membership.objects.pending(self).get(player=player)
        m.status = MEMBERSHIP_STATUS[1][0]
        m.save()

        #see if they completed the team.
        if Membership.objects.approved(self).count() >= self.size:
            self.status = TEAM_STATUS[1][0]
            self.save()

class Membership(models.Model):
    """
    Manages the teams - relation between players and teams
    """
    team = models.ForeignKey(Team)
    player = models.ForeignKey(Player)

    date_player_joined = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=3, choices=MEMBERSHIP_STATUS, 
                              default=MEMBERSHIP_STATUS[0][0])
    
    objects = MembershipManager()

    class Meta:
        db_table = 'team_members'
        unique_together = (
            ('team', 'player'),
        )

    @staticmethod
    def createMembership(player, team):
        """ Simple method shorthand for creating team """
        return Membership(team=team, player=player)

    def __unicode__(self):
        return u'%s (%s)' % (self.player, self.team)


class Tournament(models.Model):
    """
    Tounraments are a grouping of teams competing at a given date and time.
    """
    name = models.CharField(max_length=80, blank=False,
                            help_text='The visible name of the tournament')
    organized_by = models.ForeignKey(Player, related_name='tournaments_created',
                                     help_text='Creator of this tournament.')
    competing_teams = models.ManyToManyField(Team)
    time_created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=4, choices=TOURNAMENT_STATUS,
                              default=TOURNAMENT_STATUS[0][0],
                              help_text='Current status of this tournament')
    best_of = models.IntegerField(default=3, choices=BEST_OF_CHOICES,
                                  help_text='Matches required before its considered won, typically 3, 5, or 7')
    winner = models.ForeignKey(Team, blank=True, null=True,
                               related_name='+',
                               help_text='The team that one the match!')
    size = models.IntegerField(default=1, choices=TEAM_SIZES,
                               help_text='The required team size to join')

    class Meta:
        db_table = 'tournaments'

    def as_dictionary(self):
        return {
            u'name' : self.name,
            u'organized_by' : self.organized_by.name,
            u'competing_teams' : [x.as_dictionary() for x in self.competing_teams.all()],
            u'status' : self.status,
            u'best_of' : self.best_of,
        }

    def __unicode__(self):
        if not self.name:
            return u'Unnamed Tournament (%s)' % (self.competing_teams.all())
        return u'%s (%s)' % (self.name, self.competing_teams.all())


    def win_match(self, team):
        """
        When a team wins a match in a set, this method will record the victory
        by finding out the set they are in and inserting a new match record.
        If this match also decided the victor of the set, this method will
        make the apporpriate calls to win_set()
        """
        #find the teams current position in tourney
        s = self.find_teams_current_set(team)

        #if the match hasn't be "started" yet, then they are cheatin!
        if s.set_status != SET_STATUS[1][0]: #In progress..
            raise ValueError('win_match cannot promote team %s in tournament'
                             ' %s set number %d because the set is over or is' 
                             ' not ready to be started yet' % (team.name,
                             self.name, s.set_number))

        #make a new match for them to win
        m = s.matches.create(winner=team)

        #see if they won the set by couting their wins
        if s.matches.filter(winner=team).count() > (self.best_of / 2):
            self.win_set(team)
        


    def win_set(self, team):
        """
        When a team wins a set, this method will promote them to next bracket
        or win them the tournament if there are no more sets to be had.

        This method will NOT check how many matches are won, etc. win_set is 
        most likely not the call you want to use; look at win_match instead.

        Notes:
        Doesn't do much fail safe checking.  Can promote more teams to a set
        than is supported among other things...
        """

        #find there fartherest progressed match in the tournament.
        s = self.find_teams_current_set(team)

        #if they aren't in this set... then maybe its an attacker?
        if s == None:
            raise ValueError('Team \'%s\' is not in Tournament \'%s\'' %
                            (self.name))

        #they are in this tournament. lets promote them.
        #current sets status should be set to completed.
        s.set_status = SET_STATUS[2][0]
        s.winner = team
        s.save()

        #calculate next Ro Set they should jump into...
        next_set = s.set_number / 2

        #maybe the tournament is over?
        if next_set == 0:
            #yay they did it!
            self.status = TOURNAMENT_STATUS[3][0]
            self.winner = team
            self.save()
            return None

        #the tournament is not over, so put them into the next set...
        ns = self.all_sets_in_tournament.get(set_number=next_set)
        ns.competing_teams.add(team)

        #if there are two players in this next set, set it to started
        if ns.competing_teams.count() == 2:
            ns.set_status = SET_STATUS[1][0]
            ns.save()

    def demote_match(self, team):
        """
        If a match was accidently promoted when it should not have been, then
        we can demote it and restore the previous state.

        This function will delete from Match; this is intended currrently as
        it would be rare to use this feature unless it was a mistake.
        """
        s = self.find_teams_current_set(team)

        #if the set is completed, then this must be a losing team.
        if s.set_status == SET_STATUS[2][0]:
            raise ValueError('Cannot demote team \'%s\' in tournament \'%s\' '
                             ' \'%s\'' % (team.name, self.name))

        #out of all the matches in this tournament in which this team won.
        # ".order_by('-id')[0]" -- find the most recent.
        #note: maybe sorting by it won't gaurentee age of match? Maybe add
        #a date time field???
        try:
            m = Match.objects.filter(in_set__in_tournament=self, winner=team).\
                                     order_by('-id')[0]
        except:
            raise ValueError('Cannot demote team \'%s\' in tournament \'%s\'.'
                             ' No matches to remove.' % (team.name, self.name))
        #remove the offending match
        m.delete()

        #for the occasion when they were promoted to a new set but haven't
        #played a match in that set yet...
        if s != m.in_set:
            #this must have been a match that promoted them, so we need to
            #restore the state perviously to the promotion
            s.competing_teams.remove(team)
            s.set_status = SET_STATUS[0][0] #Not started yet...
            s.save()

            #now that they are out of the wrong bracket. find their previous
            #location in the tournament
            ps = self.find_teams_current_set(team)
            ps.set_status = SET_STATUS[1][0] #In progress...
            ps.save()

    def find_teams_current_set(self, team):
        """
        This method is a helper that will find out which set the team is curr-
        ently playing in.  If the team is not found, it will return None.
        """

        #even though set_number is default, make sure we get this order
        #so that we always find the farthest point this team has reached
        #in the tournament
        
        for s in self.all_sets_in_tournament.order_by('set_number'):
            if team in s.competing_teams.all():
                return s
        
        raise ValueError('Could not find team \'%s\' in tournament \'%s\'' % 
                        (team.name, self.name))

    def start_tournament(self):
        """
        Starts a tournament.
        Sets the status appropriately, and creates all the sets for the
        tournament.
        """

        #if the tournament is in progress, raise exception
        if self.status != TOURNAMENT_STATUS[0][0]:
            raise ValueError('Tournament %s was tried to be started after it '
                             'was already in progress...' % (self.name))

        #we only can start a tournament if we have a base 2 amount of players
        #later we will add elimination rounds to deal with realistic conditions
        if mod(log(self.competing_teams.count(), 2), 1) != 0:
            raise ValueError('There wasn\'t an appopriate number of teams in '
                             'tournament %s to start. (%d teams.) Needs to be'
                             ' a power of 2...' % (self.name, set_counter))

        set_counter = self.competing_teams.count() - 1
        self.status = TOURNAMENT_STATUS[2][0]
        self.save()
        
        while set_counter > 0:
            #assume that there are a log2 based amount of teams... 
            #no elmination rounds yet.
            self.all_sets_in_tournament.create(set_number=set_counter)
            set_counter -= 1

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
    """ Sets exist four tournaments. Need to keep track of the which when """
    """ matches are completed.  Each match can have as many teams as is   """
    """ needed, but the UI will only support two. """

    in_tournament = models.ForeignKey(Tournament, 
                                      related_name='all_sets_in_tournament', 
                                      help_text='From this tournament')
    set_type = models.CharField(max_length=3, choices=SET_TYPES,
                                default=SET_TYPES[1][0],
                                help_text='A status tracker for when we eventually do elmination rounds')
    set_status = models.CharField(max_length=3,  choices=SET_STATUS,
                                  default=SET_STATUS[0][0],
                                  help_text='Has it started? Is it over? Is it a placeholder?')
    winner = models.ForeignKey(Team, null=True, blank=True,
                               related_name='+',
                               help_text='The team that one this set')
    set_number = models.IntegerField(help_text='Used to represent the tournament tree aka brackets')
    competing_teams = models.ManyToManyField(Team,
                                             related_name='all_set_history', 
                                             help_text='All the teams in this match.. should be 2...')
    #
    objects = SetManager()

    class Meta:
        db_table = 'sets_in_tournaments'
        #sort by ascending by default.
        ordering = ['set_number']

class Match(models.Model):
    """ Each match is part of a set and represents a game """
    """ Maybe we can add replay file uploads and stuff later here if interested """
    """ For now this will be a dumb class, just used for select count(*) type things """
    """ so it doesn't matter which match is added or removed """
    in_set = models.ForeignKey(Set, related_name='matches', 
                               help_text='The set this was from')
    winner = models.ForeignKey(Team, null=True, blank=True,
                               related_name='+',
                               help_text='The team that one this match')

    class Meta:
        db_table = 'matches_in_set'
        ordering = ['id']

