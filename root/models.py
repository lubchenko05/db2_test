import random
import string
import smtplib

import sys
from email.mime.text import MIMEText

from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import BaseUserManager


class MyUserManager(BaseUserManager):
    """
    A custom user manager to deal with emails as unique identifiers for auth
    instead of usernames. The default that's used is "UserManager"
    """
    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    USERNAME_FIELD = 'email'
    objects = MyUserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def get_profile(self):
        return Profile.objects.get(user=self)


class Post(models.Model):
    owner = models.ForeignKey(get_user_model())
    title = models.CharField(max_length=250)
    image = models.ImageField(upload_to='Images/Posts', default='Images/None/NoPost.jpg', blank=True)
    text = models.TextField()

    def __str__(self):
        return self.title

    def get_likes(self):
        return PostLikes.objects.filter(post=self)

    def likes_count(self):
        return len(PostLikes.objects.filter(post=self))

    def is_liked(self, user):
        return True if user in [u.user for u in self.get_likes()] else False


class PostLikes(models.Model):
    post = models.ForeignKey(Post, related_name='likes')
    user = models.ForeignKey(get_user_model())

    def __str__(self):
        return self.title


class Comment(models.Model):
    owner = models.ForeignKey(get_user_model())
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return f'{self.post.title} - {self.owner.email}'


class Profile(models.Model):
    def code_generator():
        letters = string.ascii_uppercase
        return ''.join(random.choice(letters) for _ in range(8))

    user = models.OneToOneField(get_user_model(), unique=True)
    verified_email = models.BooleanField(default=False)
    verified_code = models.CharField(default=code_generator(), max_length=8)
    birthday = models.DateField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    liked_post = models.ManyToManyField(Post, 'liked_posts')

    def __str__(self):
        return f"{self.user}'s profile"


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile, created = Profile.objects.get_or_create(user=instance)
        try:
            text = '''
                Hello,

                Your verify code for test4: %s

                Regards, Yuri!
                ''' % profile.verified_code
            msg = MIMEText(text, 'plain')
            msg['Subject'] = "Verify code"
            with smtplib.SMTP('smtp.mail.ru', 465) as s:
                s.ehlo()
                s.starttls()
                s.ehlo()
                s.login('lubchenko05@mail.ru', 'ms12777NS1epXhU')
                s.sendmail('lubchenko05@gmail.ru', [instance.email, ], msg.as_string())
                s.close()
        except:
            print("Unable to send the email. Error: ", sys.exc_info()[0])

post_save.connect(create_user_profile, sender=get_user_model())


