from django.db import models
from django.db.models.signals import post_save

class Reward(models.Model):
    name = models.CharField(max_length=50)
    rank = models.IntegerField(choices={(1,1),(2,2),(3,3)}) 
    discribtion = models.TextField()
    users = models.ManyToManyField("account.User", blank=True)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

def where_to_upload(instance, filename):
    return '{0}/client.zip'.format(filename)


class Submission(models.Model):
    challenge = models.ForeignKey('challenge.Challenge', on_delete=models.CASCADE)
    user = models.ForeignKey("account.User", on_delete=models.CASCADE)
    zip_file = models.FileField(upload_to=where_to_upload, blank=True, null=True)
    
    LANGUAGE_CHOICE = {('go','Go'),('c++','C++'),('python','Python'),('java','Java'),}
    language = models.CharField(choices=LANGUAGE_CHOICE, default='python', max_length=10)
    
    COMPILE_CHOICE = { ('Eroro',-1), ('compiling',0), ('compiled',1), }
    status = models.CharField(choices=COMPILE_CHOICE, max_length=9)

    date = models.DateTimeField(auto_now=True)

    game = models.ForeignKey('challenge.Game', on_delete=models.CASCADE,default='')

    def __str__(self):
        return " ({}) : {} : {} : {} ".format(self.id , self.user, self.language, str(self.date)[:19])


class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    photo_main = models.ImageField(upload_to='photo/team/%Y/%m/%d', blank=True, null=True)
    admin = models.ForeignKey('account.User', on_delete=models.CASCADE,  related_name='admin')
    member = models.ManyToManyField("account.User", blank=True)
    score = models.ManyToManyField('challenge.Score', blank=True, related_name='members')
    submission = models.ManyToManyField("challenge.Submission",blank=True)
    message_box = models.ManyToManyField('challenge.PostMessage',blank=True)
    active = models.BooleanField(default=False)
    # challenge_history = models.ManyToManyField("challenge.Challenge")
    #game = models.ManyToManyField("challenges.Game")

    def __str__(self):
        return self.name


class Challenge(models.Model):
    name = models.CharField(max_length=50)
    discribtion = models.TextField(default=" ")
    teams = models.ManyToManyField("challenge.Team",blank=True) # همه ی تیم ها
    game = models.ManyToManyField("challenge.Game",blank=True)  # گیم ها ONE TO MANY
    Race = models.ManyToManyField("challenge.Race",blank=True)  # مسابقات
    # # laby - waiting - finished ---> must be creat dear developers
    # STATUS_CHOICE = {('laby','Laby'), ('waiting','Waiting'), ('finished','Finished')}
    # challenge_status = models.CharField(choices=STATUS_CHOICE, default='laby', max_length=50)
    
    def __str__(self):
        return self.name


class Game(models.Model):
    name = models.CharField(max_length=50, unique=True, default='game')

    def __str__(self):
        return self.name


class Race(models.Model):
    name = models.CharField(max_length=50, blank=True)
    game = models.ForeignKey("challenge.Game", on_delete=models.CASCADE)  # گیم مسابقه
    team_1 = models.ForeignKey('challenge.Team', related_name='team_1', on_delete=models.CASCADE)
    team_2 = models.ForeignKey('challenge.Team', related_name='team_2', on_delete=models.CASCADE)
    team1_result = models.IntegerField(default=0)
    team2_result = models.IntegerField(default=0)
    allow = models.BooleanField(default=False)
    # game_score = models.IntegerField(default=0) #  این مقدار به اسکور تیم ها کم یا اضاقه می شود
    
    # TYPE_CHOICE = {('tornoment','T'), ('f_normal','N'), ('f_random','R'), ('Lig','L')}
    # game_type = models.CharField(choices=TYPE_CHOICE, default='friendly', max_length=50)
    # game_map = models.CharField(blank=True,null=True,max_length=70)


    def __str__(self):
        return '{} : {} '.format(self.name, self.id)
    

def set_name(sender, instance, **kwargs):
    new_name = " {} VS {} ".format(instance.team_1.name, instance.team_2.name)
    Race.objects.filter(id = instance.id ).update(name = new_name ) 
post_save.connect(set_name, sender=Race)


class Score(models.Model):
    TYPE_CHOICE = {('frindy','F'),('Lig','L')}
    type = models.CharField(choices=TYPE_CHOICE, max_length=9)
    challenge = models.ForeignKey('challenge.Challenge', on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    pos = models.CharField(blank=True, max_length=10)

    
    def __str__(self):
        return   str(self.score)




class PostMessage(models.Model):
    message = models.CharField(max_length=100)
    data = models.CharField(max_length=100,blank=True)

    def __str__(self):
        return 'message in id : {}'.format(self.id)