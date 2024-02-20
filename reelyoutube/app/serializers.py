from rest_framework import serializers
from .models import Video
from django.contrib.auth.models import User
from django.utils import timezone

class TimeAgoField(serializers.Field):
    def to_representation(self, value):
        if not value:
            return ""
        
        now_utc = timezone.now()
        time_difference = now_utc - value

        if time_difference.days > 365:
            return f'{time_difference.days // 365} years ago'
        elif time_difference.days > 30:
            return f'{time_difference.days // 30} months ago'
        elif time_difference.days > 7:
            return f'{time_difference.days // 7} weeks ago'
        elif time_difference.days > 1:
            return f'{time_difference.days} days ago'
        elif time_difference.seconds > 3600:
            return f'{time_difference.seconds // 3600} hours ago'
        elif time_difference.seconds > 60:
            return f'{time_difference.seconds // 60} minutes ago'
        else:
            return f'{time_difference.seconds} seconds ago'


class VidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'

class VideoSerializer(serializers.ModelSerializer):
    pass
    published = TimeAgoField()

    class Meta:
        model = Video
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['author'] = instance.author.channeluser.channelname
        representation['authorslug'] = instance.author.channeluser.channelslug
        representation['subs'] = instance.author.channeluser.subscribers.all().count()
        representation['duration'] = instance.duration
        representation['views'] = instance.views
        representation['liked'] = instance.liked.all().count()
        # representation['published'] = instance.published
        representation['image'] = "http://localhost:8000"+instance.image.url
        representation['video'] = "http://localhost:8000"+instance.video.url
        representation['channelimg'] = "http://localhost:8000"+instance.author.channeluser.channelimg.url

        return representation

class UserSerializer(serializers.ModelSerializer):
    class Meta: 
        model = User
        fields = '__all__'

        def to_repren(self, instance):
            context = super().to_repren(instance)
            context['username'] = instance.username

            return context
            