from rest_framework import serializers
from challenge.models import Team, Score, Challenge, PostMessage, Submission, Race,Game
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
                if field[i][0] != user:
                    team.member.add(field[i][0])
                    text = 'Hi {user}, {admin} invited you to join {team} '.format(user=field[i][0].username, admin=team.admin, team=team.name)
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
    team = serializers.CharField()
    challenge = serializers.CharField()
    game = serializers.CharField()


    class Meta:
        model = Submission
        fields = ('challenge', 'team', 'language', 'game', 'zip_file')

    
    def submit(self, member):
        try:
            challenge = Challenge.objects.filter(name = self.validated_data['challenge'])[0]
            team = Team.objects.filter(name= self.validated_data['team'])[0]
            file = self.validated_data['zip_file']
            language = self.validated_data['language']
            game = Game.objects.filter(name = self.validated_data['game'])[0]
        except:
            result = {'response':'wrong. pleas try again'}
            return result
        if file.name[-4:] != '.zip':
            result = {'response':'your file is not zip'}
        else:
            if len(Submission.objects.all()) == 0 :
                file.name = str(1)
            else:
                file.name = str(Submission.objects.latest('id').id+1)
            submit = Submission.objects.create(
                challenge = challenge,
                user = member,
                zip_file = file,
                language = language,
                status = 'compiling',
                game = game 
            )
            data = {
                "file":submit.id,
                }
            from challenge.tasks import compile_task
            ans = compile_task.delay(data)
            if ans.result==0:
                rs = 'there is problem in submit .  please try again '
            else: 
                team.submission.add(submit)
                rs = "succes submit "
        return {'response' : rs}
        



class ChallengeRegisterSerializer(serializers.Serializer):
    team = serializers.CharField()
    challenge = serializers.CharField()

    def register_team(self, user):
        result = ""
        try:
            challenge = Challenge.objects.filter(name = self.validated_data['challenge'])[0]
            T = Team.objects.filter(name = self.validated_data['team'])[0]
            if user == T.admin and T.active == True:
                challenge.teams.add(T)
                result = 'team {} added'.format(T.name)
            else:
                result = 'you can not do this'
        except:
            result = 'except'
        return result



class CreatRace(serializers.Serializer):
    rival_team = serializers.CharField() 
    your_team = serializers.CharField()
    challenge = serializers.CharField()
    game = serializers.CharField()


    def creat(self, user):
        result = ''
        try:
            challenge = Challenge.objects.filter(name = self.validated_data['challenge'])[0]
            teams = challenge.teams.distinct() 
            rival_team = Team.objects.filter(name = self.validated_data['rival_team'])[0]
            team = Team.objects.filter(name = self.validated_data['your_team'])[0]
            games = challenge.game.distinct()
            game = Game.objects.filter(name = self.validated_data['game'])[0]
            if user != team.admin:
                result = {'response':"you are not admin of {}".format(Team.name)}
            elif game not in games:
                result = {'response':'this game is not in this challneg'}
            elif (rival_team not in teams) or (team not in teams):
                result = "shout every two team be in challenge"
            else:
                race = Race.objects.create(
                    game = game,
                    team_1 = team,
                    team_2 = rival_team
                )

                text = ' {admin} from {team} invited you to a race in {G} game '.format(admin=user.username,team=team.name, G=game.name)
                message = PostMessage.objects.create(message=text)
                link = 'http://127.0.0.1:9000/answer-to-race/{team}/{race}/{msg}'.format(team=rival_team.name, race=race.id, msg=message.id )
                message.data = link
                message.save()
                rival_team.message_box.add(message)
                result = "invite send"
        except :
            result = {'response':'wrong in exept'}
        return result


class AnswerToRaceRegister(serializers.Serializer):
    race_id = serializers.CharField()  
    msg_id = serializers.CharField()
    answer = serializers.CharField()


    def set_invite(self, team, user):       
        try: 
            T = Team.objects.filter(name = team)[0]
            ans = self.validated_data['answer']
            msg = PostMessage.objects.filter(id=self.validated_data['msg_id'])[0]
            race = Race.objects.filter(id = self.validated_data['race_id'])[0]
            # import pdb; pdb.set_trace()
            if user == T.admin:
                if ans == 'Yes':
                        race.allow = True
                        race.save()
                        text = '{team} accepted your invite'.format(team=team)
                        message = PostMessage.objects.create(message=text)
                        race.team_1.message_box.add(message)
                        msg.delete()
                        result = {'response':'invite accepted'}
                elif ans == "No":
                    text = '{team} passed your invite'.format(team)
                    message = PostMessage.objects.create(message=text)
                    race.team_1.message_box.add(message)
                    msg.delete()
                    race.delete()
                    result = {'response':'invite passes'}
            else:
                result = {'response':'you are not admin of this group'}
            return result
        except:
            result = {'response':"wrong  in except"} 
            return result

        

