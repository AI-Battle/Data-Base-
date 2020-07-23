from django.db import models
from challenge.models import Team, PostMessage
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    english_firstname = models.CharField(max_length=50)
    english_lastname = models.CharField(max_length=50)
    photo_main = models.ImageField(upload_to='photo/profile/%Y/%m/%d', blank=True)
    birthday = models.DateField(auto_now=False)
    individual_score = models.IntegerField(default=0, blank=True)
    phone_number = models.IntegerField(default=0, blank=True)
    national_id = models.IntegerField(default=0, blank=True) 
    Gender = {('Man','M'), ('Woman','W')}
    gender = models.CharField(choices=Gender, max_length=5, blank=True)
    abilites = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    message_box = models.ManyToManyField(PostMessage, blank=True, related_name='message_box')
    teams = models.ManyToManyField(Team, blank=True, related_name='teams')



