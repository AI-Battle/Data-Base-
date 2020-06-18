from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from account.models import User
from account.api.serializers import (
    RegisterationSerializer,
    UserSerializer,
)

from rest_framework.permissions import IsAuthenticated




class UserView(viewsets.ReadOnlyModelViewSet):
    # permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer





@api_view(['POST',])
def registration_view(request,):
    if request.method == 'POST':
        serializer = RegisterationSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            user  = serializer.save()
            data['response']= 'ثبت نام با موفقیت انجام شد'
            data['email'] = user.email
            data['username'] = user.username
            data['id'] = user.id
        else:
            data = serializer.errors
        return Response(data)




@api_view(['GET',])
@permission_classes([IsAuthenticated])
def flag_uses(request,user):
    data={}
    try:
        person = get_object_or_404(User, username=user)
        data["response"] = "ok"
        data["user"] = person.username
        return Response(data)
    except User.DoesNotExist:
        data["response"] = "not found"
        return Response(data, status=status.HTTP_404_NOT_FOUND)