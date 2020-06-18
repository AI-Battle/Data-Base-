from rest_framework import serializers
from account.models import User
from challenge.models import PostMessage


class RegisterationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model  = User
        fields = ['username', 'email', 'password', 'password2', 'english_firstname', 'english_lastname', 'birthday',]

        extra_kwargs = {
            'password': {'write_only' :True},
        }

    def save(self):
        user = User(
            email     = self.validated_data['email'],
            username  = self.validated_data['username'],
            birthday  = self.validated_data['birthday'],
            english_firstname = self.validated_data['english_firstname'],
            english_lastname = self.validated_data['english_lastname']

        )
        user.is_active = True
        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({'password': 'پسورد ها باید مشابه باشند !'})
        user.set_password(password)
        user.save()
        return user



class UserSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'english_lastname', 'is_active','teams' , 'message_box')



