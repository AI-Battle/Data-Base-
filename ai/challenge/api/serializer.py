from rest_framework import serializers
from challenge.models import Team, Score, Challenge, PostMessage, Submission
from account.models import User
from django.forms.fields import FileField

from rest_framework.response import Response



class TeamRegistation(serializers.ModelSerializer):
        user_field  = serializers.CharField(style={'input_type':'password'}, write_only=True)

        class Meta:
            model = Team
            fields = ('name','user_field')

        def save(self,user):
            field = [User.objects.filter(username=i) for i in self.validated_data['user_field'].split(' ')]
            team = Team.objects.create(
                name = self.validated_data['name'],
                admin = user
            )
            user.teams.add(team)
            for i in range(min(len(field),2)):
                team.member.add(field[i][0])
                text = ' {admin} invited you to join {team} '.format(admin=team.admin, team=team.name)
                link = 'http://127.0.0.1:8000/answer/{team}'.format(team=team.name)
                message = PostMessage.objects.create(message=text, data=link)
                field[i][0].message_box.add(message)
            return team
        

class InviteRegister(serializers.ModelSerializer):
    ans = serializers.CharField(max_length=3)
    id = serializers.IntegerField()

    class Meta:
        model = Team
        fields = ['ans', 'id']


    def set_invite(self, user, team):
        try:
            team = Team.objects.filter(name=team,
                member__username__iexact=user)[0]
        except:
            PostMessage.objects.get( pk = self.validated_data['id']).delete()
            raise serializers.ValidationError({'response':' چینین تیمی وجود ندارد. یا ممکن است این تیم حذف شده باشد'})
        data = {}
        if self.validated_data['ans'] == 'yes': 
            team.active = True
            user.teams.add(team)
            data['answer'] = 'عضویت شما انجام شد'
        else: 
            team.member.remove(user)
            data['answer'] = 'شما درخواست عضویت را رد کردید'
        team.save()
        PostMessage.objects.get( pk = self.validated_data['id']).delete()
        return data
        
    

class Member_Edit(serializers.ModelSerializer):
    team = serializers.CharField(max_length=100)
    member = serializers.CharField(max_length=100)

    class Meta:
        model = Team
        fields = ['team','member']
    
    def add_member(self, admin):
        T = Team.objects.filter(name=self.validated_data['team'])[0]
        field = [User.objects.filter(username=i) for i in self.validated_data['member'].split(' ')]
        l = len(T.member.distinct())
        data = {}
        if T.admin == admin and l < 2 :
            for i in range(2-l): 
                if field[i][0] not in T.member.distinct() :
                    T.member.add(field[i][0])
                    text = ' {admin} invited you to join {team} '.format(admin=T.admin, team=T.name)
                    link = 'http://127.0.0.1:8000/answer/{team}'.format(team=T.name)
                    message = PostMessage.objects.create(message=text, data=link)
                    field[i][0].message_box.add(message)
            T.save()
            data['response'] = 'درخواست برای افراد ارسال شد'
        else :
            data['response'] = 'Wrong'
        return data


    def delete_member(self, admin):
        team = Team.objects.filter(name=self.validated_data['team'])[0]
        member  = User.objects.filter( username = self.validated_data['member'])
        data = {}
        if team.admin == admin or admin == member :
            if member in team.member.distinct():
                team.member.remove(member)
                member.teams.remove(team)
                if team.admin == admin and admin == member:
                    team.delete()
                elif len(team.member.distinct()) == 0 :
                    team.active = False
                data['response'] = ' {user} با موفقیت حذف شد '.format(user=member)
            else : 
                data['response'] = 'عضو در این گروه وجود ندارد'
        else:
            data['response'] = ' اجازه انجام چنین کاری وجود ندارد'
        return data
            

class DeleteTeam(serializers.ModelSerializer):
    team = serializers.CharField(max_length=100)

    class Meta:
        model = Team
        fields = ['team']


    def delet_team(self, admin):
        team = Team.objects.filter(name=self.validated_data['team'])[0]
        data = {}
        if team.admin == admin:
            team.delete()
            data['response'] = 'تیم با موفقیت حذف شد'
        else:
            data['response'] = 'اجازه چنین کاری وجود ندارد'
            
        return data




class PostSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = PostMessage
        fields = ('id', 'message', 'data', 'url')



class TeamSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Team
        fields = ('id', 'name', 'admin', 'member', 'score', 'submission', 'active', 'message_box')

    



class ScoreSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Score
        fields = ('id', 'score', 'challenge')


class ChallengeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Challenge
        fields = ('id', 'name')






##########################################################
#################    submission     ######################
##########################################################


class SubmissionSerializer(serializers.ModelSerializer):
    
    challenge_name = serializers.CharField()
    team = serializers.CharField()
    language_name = serializers.CharField()

    class Meta:
        model = Submission
        fields = ('challenge_name', 'team', 'zip_file', 'language_name')

    # def custom_data(self):
    #     data = {
    #         'team':self.validated_data['team'],
    #         'zip_file':self.validated_data['zip_file'],
    #         'challenge_name':self.validated_data['challenge_name']
    #     }
    #     return data
    def submit(self, member="ali"):

        challenge = Challenge.objects.filter(name = self.validated_data['challenge_name'])[0]
        T = Team.objects.filter(name = self.validated_data['team'])[0]
        user = User.objects.filter(username = member)[0]  #user member
        file = self.validated_data['zip_file']
        language = self.validated_data['language_name']
        if file.name[-4:] == '.zip' and user in T.member.distinct() or user == T.admin : #and the team is in this challenge
            if len(Submission.objects.all()) == 0 :
                file.name = str(1)
            else:
                str(Submission.objects.latest('id').id+1)
            submit = Submission.objects.create(
                challenge = challenge,
                user = user,
                zip_file = file,
                language = language,
                status = 'compiling'
            )
            data = {
                "file":submit.id,
                }
            from challenge.tasks import submission_task
            ans = submission_task.delay(data)
            if ans.result==0:
                rs = {'response' : 'there is problem in submit .  please try again '}
            else: 
                rs = {"response":"succes submit "}
            return rs
        else:
            return {"response":"fail"}
        

