from django.db import models
from django.db.models.signals import post_save
# from .utils import random_slug_url
from django.utils.text import slugify
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=210)
    last_name = models.CharField(max_length=210)
    email = models.EmailField(max_length=200, unique=True)
    # slug = models.SlugField(max_length=200, blank=True, unique=True)
    avatar = models.ImageField(default='user.png', blank=True, upload_to='profile/avatar')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @property
    def get_first_name(self):
        return self.first_name

    @property
    def get_full_name(self):
        full_name = f'{self.first_name} {self.last_name}'
        return full_name
    

    @property
    def get_email(self):
        return self.email


    def save(self, *args, **kwargs):
        if self.avatar == '':
            self.avatar = 'user.png'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username

def create_the_profile(created, sender, instance, *args, **kwargs):
    if created:
        Profile.objects.create(user=instance, first_name=instance.first_name, last_name=instance.last_name, email=instance.email)
post_save.connect(create_the_profile, sender=User)