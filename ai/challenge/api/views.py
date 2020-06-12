from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from account.models import User
from challenge.models import (
    Team,
    Score,
    Challenge,
    PostMessage
)

from .serializer import (
    ScoreSerializer, 
    TeamSerializer,
    ChallengeSerializer,
    TeamRegistation,
    InviteRegister,
    Member_Edit,
    DeleteTeam,
    PostSerializer,
    SubmissionSerializer
    )


from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView








# creat team
@api_view(['POST',])
@permission_classes([IsAuthenticated])
def Teamregister(request):
    if request.method == 'POST':
        serializer = TeamRegistation(data=request.data)
        data = {}
        if serializer.is_valid():
            team = serializer.save(request.user)
            data['response'] = 'تیم با موفقیت تشکیل شد و دعوت نامه های برای اعضا فرستاده شد.'
        else:
            data = serializer.errors
        return Response(data)




#asnwer to invite
@api_view(['POST',])
@permission_classes([IsAuthenticated])
def AnswerToInvite(request, team):
    data = {}
    if request.method == 'POST':
        serializer = InviteRegister(data=request.data)
        if serializer.is_valid():
            data = serializer.set_invite(request.user, team)
            return Response(data, status=status.HTTP_200_OK)
        else:
            data['response'] = 'Wrong'
            return Response(data,status=status.HTTP_400_BAD_REQUEST)
    return Response(data, status=status.HTTP_400_BAD_REQUEST)



#add new member
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_member(request):
    data = {}
    if request.method == 'POST':
        serializer = Member_Edit(data=request.data)
        if serializer.is_valid():
            data = serializer.add_member(request.user) 
            return Response(data)
        else:
            return Response(serializer.errors)


#delete member from team with admin
@api_view(['POST',])
@permission_classes([IsAuthenticated])
def delete_member(request):
    data = {}
    if request.method == 'POST' :
        serializer = Member_Edit(data=request.data)
        if serializer.is_valid():
            data = serializer.delete(request.user)
        else:
            data = serializer.errors
    return Response(data)



#delete team
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_team(request):
    data = {}
    if request.method == 'POST':
        serializer = DeleteTeam(data=request.data)
        if serializer.is_valid():
            data = serializer.delet_team(request.user)
        else:
            data = serializer.errors
    return Response(data)


# team detail
@api_view(['GET'])
def TeamView_detail(request,pk):
    if request.method == 'GET':
        teames = Team.objects(kp=pk)
        serializer = TeamSerializer(Team, many=True)
        return Response(serializer.data)




@api_view(['GET'])
def Score_detail(request,pk):
    try:
         score = Score.objects.get(pk=pk)
    except Score.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ScoreSerializer(score,context={'request': request})
        return Response(serializer.data)








##### show all detail 


class PostMessagetView(viewsets.ReadOnlyModelViewSet):
    queryset = PostMessage.objects.all()
    serializer_class = PostSerializer


class ScoreView(viewsets.ReadOnlyModelViewSet):
    queryset = Score.objects.all()
    serializer_class = ScoreSerializer


class ChallengeView(viewsets.ReadOnlyModelViewSet):
    queryset = Challenge.objects.all()
    serializer_class = ChallengeSerializer
   

class TeamViewList(viewsets.ReadOnlyModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer







#################################################
################## submission ###################


@api_view(['POST'])
def submit_file(request):    
    if request.method == 'POST':
        serializer = SubmissionSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.submit()
            return Response(data)
    return Response({'response':'wrong'})



