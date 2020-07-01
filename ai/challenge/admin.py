from django.contrib import admin
from .models import Reward , Submission, Team, Game, Score, Challenge, Race

admin.site.register(Race)
admin.site.register(Reward)
admin.site.register(Submission)
admin.site.register(Team)
admin.site.register(Game)
admin.site.register(Score)
admin.site.register(Challenge)