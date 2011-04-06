from django.db import models

class TournamentManager(models.Manager):
    """
    Simple manager to filter sets only in this tournament.

    Ease of use type manager. May or may not be used. Undecided.
    """
    pass


class SetManager(models.Manager):
    """
    Simple mamanger to filter just the elimination rounds in Set
    """
    def by_type(self, set_type=u'reg'):
        return super(SetManager, self).\
               get_query_set().filter(set_type=set_type)

    def for_tourney(self, tournament, set_type=u'reg'):
        return self.by_type(set_type=set_type).filter(in_tournament=tournament)


class MembershipManager(models.Manager):
    """
    Simple manager to filter whos on the team, and who is not
    """
    def by_type(self, membership_status=u'app'):
        return super(MembershipManager, self).\
               get_query_set().filter(status=membership_status)

    def approved(self, team):
        """
        All members on a team that have accepted the team
        """
        return self.by_type().filter(team=team)

    def pending(self, team):
        """
        All pending players thinking about approving the team
        """
        return self.by_type(membership_status=u'pen').filter(team=team)
