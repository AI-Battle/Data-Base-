from django.urls import path,include
from . import views
from account.api import views as account_views 
from rest_framework import routers


router = routers.DefaultRouter()
router.register('challeges', views.ChallengeView, basename="challenge")
router.register('users', account_views.UserView )
router.register('message', views.PostMessagetView )
router.register('teams', views.TeamViewList)
# router.register('scorslist', views.ScoreView, basename="score")



from rest_framework_simplejwt import views as jwt_views


urlpatterns = [
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('score/<int:pk>', views.Score_detail),

    path('team/register', views.Teamregister),
    path('answer/<str:team>', views.AnswerToInvite ),
    path('addmember', views.add_member ),
    path('removemember', views.delete_member ),
    
    path('challenge-register', views.challenge_register ),
    path('create-race', views.create_race),
    path('answer-to-race/<str:team>', views.answertorace),

    path('submit', views.submit_file ),


    path('', include(router.urls)),
]
