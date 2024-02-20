from email.policy import default
from pyexpat import model
from tabnanny import verbose
from tokenize import blank_re
from django.db import models
import random
from django.contrib.auth.models import User, AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings
from requests import delete
from simple_history.models import HistoricalRecords
from moviepy.video.io.VideoFileClip import VideoFileClip

from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
from io import BytesIO
from django.core.files import File
from django.utils.text import slugify
import os
from django.utils import timezone


def random_string_generator():
    characters = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    result = ''
    for i in range(0, 10):
        result += random.choice(characters)
    return result


Choices = (
    ('Public', 'Public'),
    ('Unlisted', 'Unlisted'),
    ('Private', 'Private'),
)


class Video(models.Model):
    id = models.CharField(
        max_length=255, default=random_string_generator, primary_key=True)
    visibility = models.CharField(
        choices=Choices, default='Public', max_length=100)
    title = models.CharField(max_length=1000, null=True, blank=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='image', null=True, blank=True)
    video = models.FileField(upload_to='videos', null=True, blank=True)
    duration = models.CharField(max_length=255, null=True, blank=True)
    gif = models.ImageField(upload_to='gifs/', null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    published = models.DateTimeField(auto_now_add=True, null=True)
    views = models.PositiveIntegerField(default=0, blank=True, null=True)
    liked = models.ManyToManyField(
        User, related_name='liked', null=True, blank=True)
    watchlater = models.ManyToManyField(
        User, null=True, blank=True, related_name='watchlater')

    def __str__(self):
        return str(self.id)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.duration and self.video or not self.duration:
            clip = VideoFileClip(self.video.path)
            total_seconds = int(clip.duration)
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            if hours > 0:
                self.duration = f'{hours:02}:{minutes:02}:{seconds:02}'
            else:
                self.duration = f'{minutes:02}:{seconds:02}'
            
            super().save(*args, **kwargs)




def random_channelid_generator():
    characters = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    result = 'UC'
    for i in range(0, 15):
        result += random.choice(characters)
    return result


class Channel(models.Model):
    id = models.CharField(
        max_length=100, default=random_channelid_generator, primary_key=True)
    channelname = models.CharField(max_length=255, null=True, blank=True)
    channeluser = models.OneToOneField(
        User, related_name='channeluser', on_delete=models.CASCADE, null=True)
    channelslug = models.CharField(max_length=255, blank=True, null=True)
    channelimg = models.ImageField(
        upload_to='channeluser_img', null=True, blank=True)
    channeldescription = models.TextField(blank=True, null=True)
    banner = models.ImageField(upload_to='banner', blank=True, null=True)
    subscribers = models.ManyToManyField(
        User, related_name='subscribers', null=True, blank=True)
    joined = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    history = models.ManyToManyField(
        Video, related_name='history_user', null=True, blank=True)
    twitter_url = models.CharField(max_length=9999, blank=True, null=True)
    facebook_url = models.CharField(max_length=9999, blank=True, null=True)
    instagram_url = models.CharField(max_length=9999, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.channelslug:
            self.channelslug = self.channelname.replace(' ', '')
        super().save(*args, **kwargs)

    def __str__(self):
        return (str(self.id))


def random_commentid_generator():
    characters = '0123456789'
    result = ''
    for i in range(0, 16):
        result += random.choice(characters)
    return result


class Comment(models.Model):
    comment_id = models.CharField(
        max_length=255, blank=True, default=random_commentid_generator, primary_key=True)
    comment_user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    comment_video = models.ForeignKey(
        Video, on_delete=models.CASCADE, null=True, blank=True)
    comment_body = models.CharField(blank=True, null=True, max_length=9999)

    def __str__(self):
        return str(self.comment_user)+" commented on "+str(self.comment_video.title)


class something(models.Model):
    comment_id = models.CharField(
        max_length=255, default=random_commentid_generator, blank=True, null=True)
    comment_user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    comment_video = models.ForeignKey(
        Video, on_delete=models.CASCADE, null=True, blank=True)
    comment_body = models.CharField(null=True, max_length=9999)
    comment_like = models.ManyToManyField(
        User, related_name='comment_like', null=True, blank=True)
    commented_on = models.DateTimeField(auto_now_add=True, null=True)
    comment_liked = models.BooleanField(default=False)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return 'Video: '+str(self.comment_video)+' | Commenter:'+str(self.comment_user)

    def serialize(self):
        return {
            "id": self.id,
            "comment_user": self.comment_user.serialize(),
            "body": self.comment_body,
            "post": self.comment_video,
        }

    @property
    def children(self):
        return something.objects.filter(parent=self).order_by('-commented_on')

    @property
    def is_parent(self):
        if self.parent is None:
            return True
        return False
    
    def save(self, *args, **kwargs):
        creating = self.pk is None  # Check if comment is being created (not updated)
        super().save(*args, **kwargs)
        if creating:
            if self.comment_user != self.comment_video.author:
                Notification.objects.create(
                    notification_type=3,
                    to_user=self.comment_video.author,  # Assuming you have an author field in Video
                    from_user=self.comment_user,
                    post=self.comment_video,
                    comment=self,
                )


class Notification(models.Model):
    notification_type = models.IntegerField()
    to_user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name='to_user')
    from_user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name='from_user')
    post = models.ForeignKey(
        Video, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(something, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)

    def __str__(self):
        return str(self.notification_type) + ' | ' + str(self.is_seen)


class Playlist(models.Model):
    playlist_user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    playlist_name = models.CharField(max_length=255, null=True, blank=True)
    playlist_visibility = models.CharField(
        choices=Choices, default='Public', blank=True, max_length=255)
    playlist_videos = models.ManyToManyField(
        Video, related_name='playlist_vidoes')
    playlist_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return str(self.playlist_name)



class HistoryVideo(models.Model):
    his_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    his_video = models.ForeignKey(Video, on_delete=models.CASCADE, null=True, blank=True)
    his_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return str(self.his_user.channeluser.channelname) + ' watched ' + str(self.his_video.title)
    


# @receiver(post_save, sender=HistoryVideo)
# def update_video_last_watched(sender, instance, **kwargs):
#     instance.his_video.his_time = instance.his_time
#     instance.his_video.save()


class Shorts(models.Model):
    short_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    short_video = models.FileField(null=True, blank=False, upload_to='shorts')

    def __str__(self):
        return str(self.short_user)