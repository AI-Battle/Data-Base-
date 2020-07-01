from rest_framework.permissions import BasePermission
from challenge.models import Submission, Challenge,Team, Game


class SubmitOneCode(BasePermission):
    """
    Allows if user submited one code for this game
    """
    message = 'at the first you shoud submite code for this game'

    def has_permission(self, request, view):
        team  = Team.objects.filter(name=request.data['your_team'])[0]
        game = Game.objects.filter(name=request.data['game'])[0]
        # submission = Submission.objects.filter(challenge=, game=,user=)
        for i in team.submission.distinct():
            if i.game == game:
                return True
        return False



class Registred(BasePermission):
    """
    Allow if user in this team and team be in this challenge
    """
    message = 'you can not submit code '

    def has_permission(self, request, view):
        team  = Team.objects.filter(name=request.data['team'])[0]
        challenge = Challenge.objects.filter(name=request.data['challenge'])
        if request.user == team.admin or request.user in team.member.distinct():
            return True
        return False