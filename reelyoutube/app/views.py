import random
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from datetime import date
from multiprocessing import context
from urllib import response
from django.conf import settings
from django.http import Http404, HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from .forms import ChannelCreateForm, CommentForm
from .models import Channel, Notification, Video, Comment, something, Playlist, HistoryVideo, Shorts
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate
from django.db.models import Q
from .serializers import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.db.models.expressions import Case, When
from django.views import View
import datetime
from django.forms.models import model_to_dict
import json
from django.core import serializers
from django.core import serializers
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage
from django.template import engines
from django.utils.timezone import now


def format_views_as_K(value):
    if value >= 10 ** 9:  # 1 Billion and above
        return f'{value / 10 ** 9:.1f}B'
    elif value >= 10 ** 6:  # 1 Million and above
        return f'{value / 10 ** 6:.1f}M'
    elif value >= 10 ** 3:  # 1 Thousand and above
        return f'{value / 10 ** 3:.1f}K'
    else:
        return str(value)


def time_ago(value):
    if not value:
        return ""

    now_utc = now()
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


def format_views_as_comma(value):
    return "{:,}".format(value)


def video_title_suggestions(request):
    user_input = request.GET.get('input', '').strip()
    suggestions = []

    if user_input:
        videos = Video.objects.filter(title__icontains=user_input)[:10]
        suggestions = [{'id': video.id, 'title': video.title}
                       for video in videos]

    return JsonResponse({'suggestions': suggestions})


def load_articles(request):
    articles = Video.objects.all()

    data = [{'id': article.id, 'visibility': article.visibility, 'title': article.title, 'author': article.author.username, 'image': article.image.url, 'video': article.video.url,
             'duration': article.duration, 'description': article.description, 'published': article.published, 'views': article.views} for article in articles]

    return JsonResponse({'videos': data})


def format_video_views(views):
    return "{:,}".format(views)


class ReactView(APIView):
    def get(self, request):
        video = Video.objects.all().order_by("?")
        serializer = VideoSerializer(video, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = VideoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)


class UserView(APIView):
    def get(self, request):
        user = User.objects.all()
        serializer = UserSerializer(user, many=True)
        return Response(serializer.data)


class VideoView(APIView):
    def get_object(self, id):
        try:
            return Video.objects.get(id=id)
        except Video.DoesNotExist:
            return Response("object requested does not exists", status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, id):
        video = self.get_object(id)
        serializer = VideoSerializer(video)
        return Response(serializer.data)


def home(request):
    videos = Video.objects.filter(visibility='Public').all().order_by('?')
    subscribers = ''
    notifications = ''

    articles = Video.objects.all()
    serialized_events = serializers.serialize('json', articles)

    comments = something.objects.filter(comment_video__in=videos).all()

    if request.user.is_authenticated:
        subscribers = Channel.objects.filter(subscribers=request.user).all()
        notifications = Notification.objects.filter(to_user=request.user, is_seen=False).all().order_by('-date')
    form = ChannelCreateForm()
    if request.method == 'POST':
        form = ChannelCreateForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            form.save()
            return redirect('channel', request.user.channeluser.id)

    some = something.objects.all()
    context = {
        'subscribers': subscribers,
        'videos': videos,
        'form': form,
        'notifications': notifications,
        'comments': comments,
    }
    return render(request, 'home.html', context)


def shorts(request):
    return render(request, 'shorts.html', {'shorts': shorts})


def explore(request):
    subscribers = ''
    notifications = ''
    videos = Video.objects.all().order_by('-views')[:100]
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(to_user=request.user, is_seen=False).all().order_by('-date')
        subscribers = Channel.objects.filter(subscribers=request.user).all()

    context = {
        'videos': videos,
        'subscribers': subscribers,
        'notifications': notifications,
    }
    return render(request, 'explore.html', context)


def subscriptions(request):
    subscribers = ''
    notifications = ''
    # if request.user.is_authenticated:
    #     sub = Channel.objects.filter(subscribers=request.user).all()
    #     subscribers = Channel.objects.filter(subscribers=request.user).all()
    #     notifications = Notification.objects.filter(to_user=request.user, is_seen=False).all().order_by('-date')
    # for i in sub:
    #     ids.append(i.channeluser)

    # preserved = Case(*[When(id=id, then=pos) for pos, id in enumerate(ids)])
    # vids = Video.objects.filter(author__in=ids).order_by(preserved)

    if request.user.is_authenticated:
        sub_channels = Channel.objects.filter(subscribers=request.user)
        sub_videos = Video.objects.filter(
            author__channeluser__in=sub_channels).all()

    context = {
        'vids': sub_videos,
        'subscribers': subscribers,
        'notifications': notifications,
    }
    return render(request, 'subscriptions.html', context)


def library(request):
    users = ''
    liked_videos = ''
    subscribers = ''
    notifications = ''
    watchlatervideos = ''
    playlists = ''
    if request.user.is_authenticated:
        users = HistoryVideo.objects.filter(
            his_user=request.user).all().order_by('-his_time')
        liked_videos = Video.objects.filter(liked=request.user).all()
        watchlatervideos = Video.objects.filter(watchlater=request.user).all()
        playlists = Playlist.objects.filter(playlist_user=request.user).all()
        profile = get_object_or_404(Channel, channeluser=request.user)
        subscribers = Channel.objects.filter(subscribers=request.user).all()
        notifications = Notification.objects.filter(
            to_user=request.user, is_seen=False).all().order_by('-date')

    context = {
        'users': users,
        'liked_videos': liked_videos,
        'watchlatervideos': watchlatervideos,
        'playlists': playlists,
        'subscribers': subscribers,
        'notifications': notifications,
    }
    return render(request, 'library.html', context)


def history(request):
    users = ''
    subscribers = ''
    notifications = ''
    hisvideos = ''
    if request.user.is_authenticated:
        profile = get_object_or_404(Channel, channeluser=request.user)
        users = profile.history.all()
        hisvideos = HistoryVideo.objects.filter(his_user=request.user).all().order_by('-his_time')
        subscribers = Channel.objects.filter(subscribers=request.user).all()
        notifications = Notification.objects.filter(
            to_user=request.user, is_seen=False).all().order_by('-date')

    context = {
        'users': users,
        'subscribers': subscribers,
        'notifications': notifications,
        'hisvideos': hisvideos,
    }
    return render(request, 'history.html', context)


def watch(request, id):
    video = get_object_or_404(Video, id=id)
    # title_videos = Video.objects.filter(title__icontains=video.title).exclude(id=video.id).all()
    # author_videos = Video.objects.filter(author=video.author).exclude(id=video.id).all()
    # description_videos = Video.objects.filter(description__icontains=video.description).exclude(id=video.id).all()

    somes = Video.objects.exclude(id=video.id).all().order_by("?")

    # videos = list(author_videos) + list(title_videos) + list(description_videos)
    videos = somes
    # random.shuffle(videos)

    history_video = HistoryVideo.objects.filter(
        his_user=request.user, his_video=video).first()
    if history_video:
        history_video.his_time = timezone.now()
        history_video.save()
    else:
        HistoryVideo.objects.create(
            his_user=request.user, his_video=video, his_time=timezone.now())

    notif_id = request.POST.get('v')
    if notif_id:
        notif_id = request.POST.get('v')
        notifs = Notification.objects.filter(post=video, id=notif_id).first()
        if notifs:
            notifs.is_seen = True
            notifs.save()



    if request.user.is_authenticated:
        video.views += 1
        video.save()
        notifications = Notification.objects.filter(
            to_user=request.user, is_seen=False).all().order_by('-date')
        profile = get_object_or_404(
            Channel, channeluser=request.user.channeluser.channeluser)
        if video not in profile.history.all():
            profile.history.add(video)


    context = {
        'id': id,
        'video': video,
        'videos': videos,
        'comments': comments,
        'notifications': notifications,
    }
    return render(request, 'watch.html', context)


def likes_count(request, id):
    video = get_object_or_404(Video, id=id)
    count = video.liked.all().count()
    return JsonResponse(data={'likes_count': count})


def get_comments(request, id):
    video = get_object_or_404(Video, id=id)
    comments = something.objects.filter(
        comment_video=video).all().order_by('-commented_on')
    data = list(comments.values())
    return JsonResponse(data, safe=False)


class LikeNotification(View):
    def get(self, request, id, *args, **kwargs):
        notification = Notification.objects.get(pk=id)
        notification.is_seen = True
        notification.save()

        return redirect('watch')


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
        else:
            return redirect('login')
    return render(request, 'login.html')


def search(request):
    query = request.GET.get('q')
    videos = Video.objects.filter(Q(title__icontains=query) | Q(description__icontains=query)).all()
    users = Channel.objects.filter(channelname__icontains=query).all()
    vids = ''
    for user in users:
        if user in Channel.objects.filter():
            vids = Video.objects.filter(author=user.channeluser)
    subscribers = Channel.objects.filter(subscribers=request.user).all()
    notifications = Notification.objects.filter(to_user=request.user, is_seen=False).all().order_by('-date')

    context = {
        'videos': videos,
        'query': query,
        'users': users,
        'vids': vids,
        'subscribers': subscribers,
        'notifications': notifications
    }
    return render(request, 'search.html', context)


def channel(request, id):
    featured = Video.objects.filter(
        author=request.user).order_by('-views').first()
    user = get_object_or_404(Channel, id=id)
    user_videos = Video.objects.filter(author=request.user).all()
    subscribers = Channel.objects.filter(subscribers=request.user).all()
    notifications = Notification.objects.filter(
        to_user=request.user, is_seen=False).all().order_by('-date')
    user_videos_count = user_videos.count()

    context = {'user_videos': user_videos, 'featured': featured, 'user': user,
               'subscribers': subscribers, 'notifications': notifications, 'user_videos_count': user_videos_count}
    return render(request, 'channel/channel_home.html', context)


def channel_videos(request, id):
    featured = Video.objects.filter(author=request.user).first()
    user = get_object_or_404(Channel, id=id)
    user_videos = Video.objects.filter(author=request.user).all()
    subscribers = Channel.objects.filter(subscribers=request.user).all()
    notifications = Notification.objects.filter(
        to_user=request.user, is_seen=False).all().order_by('-date')
    user_videos_count = user_videos.count()

    context = {'user_videos': user_videos, 'featured': featured, 'user': user,
               'subscribers': subscribers, 'notifications': notifications, 'user_videos_count': user_videos_count}
    return render(request, 'channel/channel_videos.html', context)


def channel_playlists(request, id):
    playlists = Playlist.objects.filter(playlist_user=request.user).all()
    notifications = Notification.objects.filter(
        to_user=request.user, is_seen=False).all().order_by('-date')
    subscribers = Channel.objects.filter(subscribers=request.user).all()
    user = get_object_or_404(Channel, id=id)
    user_videos_count = Video.objects.filter(author=request.user).all().count()

    context = {
        'user': user,
        'playlists': playlists,
        'notifications': notifications,
        'subscribers': subscribers,
        'user_videos_count': user_videos_count
    }
    return render(request, 'channel/channel_playlists.html', context)


def channel_channels(request, id):
    playlists = Playlist.objects.filter(playlist_user=request.user).all()
    user = get_object_or_404(Channel, id=id)
    channels = Channel.objects.filter(subscribers=user.channeluser).all()
    notifications = Notification.objects.filter(
        to_user=request.user, is_seen=False).all().order_by('-date')
    subscribers = Channel.objects.filter(subscribers=request.user).all()
    user_videos_count = Video.objects.filter(author=request.user).all().count()

    context = {
        'user': user,
        'playlists': playlists,
        'channels': channels,
        'notifications': notifications,
        'subscribers': subscribers,
        'user_videos_count': user_videos_count
    }
    return render(request, 'channel/channel_channels.html', context)


def channel_about(request, id):
    user = get_object_or_404(Channel, id=id)
    user_videos = Video.objects.filter(author=request.user).all()
    subscribers = Channel.objects.filter(subscribers=request.user).all()
    notifications = Notification.objects.filter(
        to_user=request.user, is_seen=False).all().order_by('-date')
    views = Video.objects.filter(author=request.user).all()
    user_videos_count = user_videos.count()
    count = 0
    for i in views:
        count += i.views

    context = {
        'count': count,
        'user_videos': user_videos,
        'user': user,
        'subscribers': subscribers,
        'notifications': notifications,
        'user_videos_count': user_videos_count
    }
    return render(request, 'channel/channel_about.html', context)


@csrf_exempt
def subscribe(request, channelslug):
    subchannel = get_object_or_404(Channel, channelslug=channelslug)
    if request.user.is_authenticated:
        if request.method == 'PUT':
            if request.user not in subchannel.subscribers.all():
                subchannel.subscribers.add(request.user)
                notify = Notification.objects.create(
                    notification_type=2, from_user=request.user, to_user=subchannel.channeluser)
                notify.save()
                return HttpResponseRedirect('', channelslug)


@csrf_exempt
def unsubscribe(request, channelslug):
    subchannel = get_object_or_404(Channel, channelslug=channelslug)
    if request.user.is_authenticated:
        if request.method == 'PUT':
            if request.user in subchannel.subscribers.all():
                subchannel.subscribers.remove(request.user)
                return HttpResponseRedirect('', channelslug)


@csrf_exempt
def watchsubscribe(request, id, channelname):
    video = get_object_or_404(Video, id=id)
    subchannel = get_object_or_404(Channel, channelname=channelname)
    if request.user.is_authenticated:
        if request.method == 'POST':
            if request.user not in subchannel.subscribers.all():
                subchannel.subscribers.add(request.user)
                notify = Notification.objects.create(
                    notification_type=2, from_user=request.user, to_user=subchannel.channeluser)
                notify.save()
                return HttpResponseRedirect('')


@csrf_exempt
def watchunsubscribe(request, id, channelname):
    video = get_object_or_404(Video, id=id)
    subchannel = get_object_or_404(Channel, channelname=channelname)
    if request.user.is_authenticated:
        if request.method == 'POST':
            if request.user in subchannel.subscribers.all():
                subchannel.subscribers.remove(request.user)
                return HttpResponseRedirect('')


def author_channel(request, channelslug):
    channel = get_object_or_404(Channel, channelslug=channelslug)
    author_videos = Video.objects.filter(author=channel.channeluser).all()
    featured = Video.objects.filter(author=channel.channeluser).first()
    subscribers = Channel.objects.filter(subscribers=request.user).all()
    notifications = Notification.objects.filter(
        to_user=request.user, is_seen=False).all().order_by('-date')


    notif_id = request.POST.get('v')
    if notif_id:
        notif_id = request.POST.get('v')
        notifs = Notification.objects.filter(
            from_user=channel.channeluser, id=notif_id).first()
        notifs.is_seen = True
        notifs.save()
    # notif = Notification.objects.get(to_user=request.user, is_seen=False).update(is_seen=True)
    # notif = Notification.objects.filter(to_user=request.user, notification_type=2).first()

    context = {
        'channel': channel,
        'author_videos': author_videos,
        'featured': featured,
        'subscribers': subscribers,
        'notifications': notifications,
    }
    return render(request, 'authorchannel/author_channel_home.html', context)


def author_channel_playlists(request, channelslug):
    channel = get_object_or_404(Channel, channelslug=channelslug)
    playlists = Playlist.objects.filter(
        playlist_user=channel.channeluser).all()

    context = {
        'playlists': playlists,
        'channel': channel,
    }
    return render(request, 'authorchannel/author_channel_playlists.html', context)


def author_channel_channels(request, channelslug):
    channel = get_object_or_404(Channel, channelslug=channelslug)
    playlists = Playlist.objects.filter(
        playlist_user=channel.channeluser).all()
    channels = Channel.objects.filter(subscribers=channel.channeluser).all()
    context = {
        'playlists': playlists,
        'channel': channel,
        'channels': channels,
    }
    return render(request, 'authorchannel/author_channel_channels.html', context)


def author_channel_videos(request, channelslug):
    channel = get_object_or_404(Channel, channelslug=channelslug)
    author_videos = Video.objects.filter(author=channel.channeluser).all()
    featured = Video.objects.filter(author=channel.channeluser).first()
    subscribers = Channel.objects.filter(subscribers=request.user).all()
    notifications = Notification.objects.filter(
        to_user=request.user, is_seen=False).all().order_by('-date')

    context = {
        'channel': channel,
        'author_videos': author_videos,
        'featured': featured,
        'subscribers': subscribers,
        'notifications': notifications,
    }
    return render(request, 'authorchannel/author_channel_videos.html', context)


def author_channel_about(request, channelslug):
    channel = get_object_or_404(Channel, channelslug=channelslug)
    author_videos = Video.objects.filter(author=channel.channeluser).all()
    featured = Video.objects.filter(author=channel.channeluser).first()
    subscribers = Channel.objects.filter(subscribers=request.user).all()
    notifications = Notification.objects.filter(
        to_user=request.user, is_seen=False).all().order_by('-date')
    count = 0
    for i in author_videos:
        count += i.views

    context = {
        'channel': channel,
        'author_videos': author_videos,
        'featured': featured,
        'subscribers': subscribers,
        'notifications': notifications,
        'count': count,
    }
    return render(request, 'authorchannel/author_channel_about.html', context)


@csrf_exempt
def like(request, id):
    user = request.user
    video = get_object_or_404(Video, id=id)
    if request.user.is_authenticated:
        if request.method == 'PUT':
            if user not in video.liked.all():
                video.liked.add(user)
                if request.user != video.author:
                    notif = Notification.objects.create(
                        notification_type=1, to_user=video.author, from_user=user, post=video, is_seen=False)
                    notif.save()
                return HttpResponseRedirect('')


@csrf_exempt
def unlike(request, id):
    user = request.user
    video = get_object_or_404(Video, id=id)
    if request.user.is_authenticated:
        if request.method == 'PUT':
            if user in video.liked.all():
                video.liked.remove(user)
                if request.user != video.author:
                    notif = Notification.objects.filter(
                        notification_type=1, to_user=video.author, from_user=user, post=video)
                    notif.delete()
                return HttpResponseRedirect('')


def notifications(request):
    notifications = Notification.objects.filter(
        to_user=request.user, is_seen=False).all()
    context = {
        'notifications': notifications,
    }
    return render(request, 'notifications.html', context)


def liked_videos(request):
    likedvideos = Video.objects.filter(liked=request.user).all()
    viewcount = 0
    for i in likedvideos:
        viewcount += i.views
    totalvideos = likedvideos.count
    likedfirst = Video.objects.filter(liked=request.user).all()[:1]
    if request.user.is_authenticated:
        subscribers = Channel.objects.filter(subscribers=request.user).all()
    context = {
        'likedvideos': likedvideos,
        'likedfirst': likedfirst,
        'totalvideos': totalvideos,
        'viewcount': viewcount,
        'subscribers': subscribers
    }
    return render(request, 'liked_videos.html', context)


def watchlater_videos(request):
    likedvideos = Video.objects.filter(watchlater=request.user).all()
    viewcount = 0
    for i in likedvideos:
        viewcount += i.views
    totalvideos = likedvideos.count
    likedfirst = Video.objects.filter(watchlater=request.user).all()[:1]
    if request.user.is_authenticated:
        subscribers = Channel.objects.filter(subscribers=request.user).all()
    context = {
        'likedvideos': likedvideos,
        'likedfirst': likedfirst,
        'totalvideos': totalvideos,
        'viewcount': viewcount,
        'subscribers': subscribers,
    }
    return render(request, 'watchlater_videos.html', context)


@csrf_exempt
def like_comment(request, id, comment_id):
    user = request.user
    comment = get_object_or_404(something, comment_id=comment_id)
    if request.method == 'PUT':
        if request.user not in comment.comment_like.all():
            comment.comment_like.add(user)
            return HttpResponseRedirect('')


@csrf_exempt
def unlike_comment(request, id, comment_id):
    user = request.user
    comment = get_object_or_404(something, comment_id=comment_id)
    if request.method == 'PUT':
        if request.user in comment.comment_like.all():
            comment.comment_like.remove(user)
            return HttpResponseRedirect('')


@csrf_exempt
def delete_comment(request, id, comment_id):
    user = request.user
    video = get_object_or_404(Video, id=id)
    comment = get_object_or_404(something, comment_id=comment_id)
    if request.method == 'PUT':
        comment.delete()
        return HttpResponseRedirect('')


def nointernet(request):
    return render(request, 'nointernet.html')


def get_video(request, id):
    try:
        video = Video.objects.get(id=id)
        video.views += 1
        video.save()
        user_liked = request.user in video.liked.all()
        contain_videos = Video.objects.filter(Q(title__icontains=video.title) | Q(description__icontains=video.description) | Q(author=video.author)).exclude(id=video.id).all()
        
        user_subscribed = request.user in video.author.channeluser.subscribers.all()
        history_video = HistoryVideo.objects.filter(his_user=request.user, his_video=video).first()
        if history_video:
            history_video.his_time = timezone.now()
            history_video.save()
        else:
            HistoryVideo.objects.create(his_user=request.user, his_video=video, his_time=timezone.now())

        comments = something.objects.filter(comment_video=video.id).all()



        videos_dict = [{
            'id': video.id,
            'title': video.title,
            'author': video.author.channeluser.channelname,
            'authorimg': 'http://localhost:8000'+video.author.channeluser.channelimg.url,
            'image': 'http://localhost:8000'+video.image.url,
            'duration': video.duration,
            'views': format_views_as_K(video.views),
            'published': time_ago(video.published),
            'description': video.description,
        } for video in contain_videos]
        video_data = {
            'id': video.id,
            'title': video.title,
            'image': 'http://localhost:8000'+video.image.url,
            'video': 'http://localhost:8000/'+video.video.url,
            'duration': video.duration,
            'views': format_views_as_comma(video.views),
            'liked': video.liked.all().count(),
            'published': time_ago(video.published),
            'description': video.description,

            'channelsl': video.author.channeluser.channelslug,

            'author': video.author.channeluser.channelname,
            'authorimg': 'http://localhost:8000/'+video.author.channeluser.channelimg.url,
            'authorsubs': video.author.channeluser.subscribers.all().count(),

            'comments': list(comments.values()),
            'commentscount': comments.count()
        }
        random.shuffle(videos_dict)
        response_list ={
            'video_data': video_data,
            'user_liked': user_liked,
            'user_subscribed': user_subscribed,
            'videos_dict': videos_dict,
        }

        return JsonResponse(response_list, safe=False)
    except Video.DoesNotExist:
        return JsonResponse({'error': 'video not found'}, status=404)










def videosapi(request):
    videos = Video.objects.all()

    videos_list = [{
        'id': video.id,
        'author': video.author.channeluser.channelname,
        'title': video.title,
        'authorslug': video.author.channeluser.channelslug,
        'subs': video.author.channeluser.subscribers.all().count(),
        'duration': video.duration,
        'views': format_views_as_K(video.views),
        'liked': video.liked.all().count(),
        'image': 'http://localhost:8000'+video.image.url,
        'video': 'http://localhost:8000'+video.video.url,
        'channelimg': 'http://localhost:8000'+video.author.channeluser.channelimg.url,
        'published': time_ago(video.published),
    } for video in videos]
    return JsonResponse(videos_list, safe=False)















@api_view(['GET'])
def get_user_data(request):
    user = request.user

    if user.is_authenticated:
        user_videos = Video.objects.filter(author=user).all()
        channel = get_object_or_404(Channel, channeluser=user)

        subscribers = Channel.objects.filter(subscribers=user.id).all()[:6]
        
        playlists = Playlist.objects.filter(playlist_user=user)
        playlist_data = [{
            'id': play.id,
            'playlistvisibility': play.playlist_visibility,
            'playlistuser': play.playlist_user.channeluser.channelname,
            'playlistname': play.playlist_name,
            'playlistvideos': list(play.playlist_videos.all().values()),
        } for play in playlists]

        total_views = 0
        for i in user_videos:
            total_views += i.views

        subscriber_data = [{
            'id': sub.id,
            'name': sub.channeluser.channeluser.channelname,
            'image': 'http://localhost:8000'+sub.channeluser.channeluser.channelimg.url,
            'slug': sub.channeluser.channeluser.channelslug,
            'subs': len(sub.channeluser.channeluser.subscribers.all()),
        } for sub in subscribers]

        user_data = {
                'username': user.username,
                'email': user.email,
                'channeluser': user.channeluser.channelname,
                'channelimage': 'http://localhost:8000'+user.channeluser.channelimg.url,
                'channelid': user.channeluser.id,
                'channelbanner': 'http://localhost:8000/'+user.channeluser.banner.url,
                'channelslug': user.channeluser.channelslug,
                'subscribers': user.channeluser.subscribers.all().count(),
                'description': user.channeluser.channeldescription,
                'joined': time_ago(user.channeluser.joined),
                'videoslength': len(Video.objects.filter(author=user).all()),
                'total_views': format_views_as_comma(total_views),
                'subscribers': subscriber_data,
                'playlist_data': playlist_data
        }

        json_list = {
            'user': user_data
        }
        response = JsonResponse(json_list)
        response['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        return response
    else:
        return Response({'status': 'user is not authenticated'})
    



def explore_videos(request):
    user = request.user
    videos = Video.objects.all().order_by('-views')[:100]
    user_channels = Channel.objects.filter(subscribers=user.id).all()

    video_list = []
    for video in videos:
        video_dict = {
            'id': video.id,
            'title': video.title,
            'author': video.author.channeluser.channelname,
            'authorimg': 'http://localhost:8000'+video.author.channeluser.channelimg.url,
            'image': 'http://localhost:8000'+video.image.url,
            'duration': video.duration,
            'views': format_views_as_K(video.views),
            'published': time_ago(video.published),
            'description': video.description,
        }
        video_list.append(video_dict)

    some_list = {
        'video_list': video_list,
    }
    
    return JsonResponse(some_list, safe=False)









def user_channel_json(request, channelslug):
    channel = get_object_or_404(Channel, channelslug=channelslug)
    videos = Video.objects.filter(author=channel.channeluser).all()
    subscribers = Channel.objects.filter(subscribers=channel.channeluser.id).all()[:6]
    playlists = Playlist.objects.filter(playlist_user=channel.channeluser)
    total_views = 0

    for i in videos:
        total_views += i.views

    subscriber_data = [{
        'id': sub.id,
        'name': sub.channeluser.channeluser.channelname,
        'image': 'http://localhost:8000'+sub.channeluser.channeluser.channelimg.url,
        'slug': sub.channeluser.channeluser.channelslug,
        'subs': len(sub.channeluser.channeluser.subscribers.all()),
    } for sub in subscribers]

    
    playlist_data = [{
        'id': play.id,
        'playlistvisibility': play.playlist_visibility,
        'playlistuser': play.playlist_user.channeluser.channelname,
        'playlistname': play.playlist_name,
        'playlistvideos': list(play.playlist_videos.all().values()),
    } for play in playlists]

    videos = [{
        'id': video.id,
        'title': video.title,
        'author': video.author.channeluser.channelname,
        'authorimg': 'http://localhost:8000'+video.author.channeluser.channelimg.url,
        'image': 'http://localhost:8000'+video.image.url,
        'duration': video.duration,
        'views': format_views_as_K(video.views),
        'published': time_ago(video.published),
        'description': video.description,
    } for video in videos ]

    user_data = {
        'id': channel.id,
        'name': channel.channelname,
        'slug': channel.channelslug,
        'banner': 'http://localhost:8000'+channel.banner.url,
        'image': 'http://localhost:8000'+channel.channelimg.url,
        'subscribers': channel.subscribers.all().count(),
        'videoslength': len(Video.objects.filter(author=channel.channeluser).all()),
        'description': channel.channeldescription,
        'joined': time_ago(channel.joined),
        'total_views': format_views_as_comma(total_views),
        'videos': videos,
        'subscriber_data': subscriber_data,
        'playlist_data': playlist_data,
    }
    return JsonResponse(user_data, safe=False)



def author_channel_json(request, channelslug):
    user = get_object_or_404(Channel, channelslug=channelslug)
    videos = Video.objects.filter(author=user.channeluser).all()
    subscribed_channels = Channel.objects.filter(subscribers = user.channeluser.id).all()
    plays = Playlist.objects.filter(playlist_user=user.channeluser)
    totalviews = 0

    for i in videos:
        totalviews += i.views

    
    subscriber_channels = [{
        'id': sub.id,
        'name': sub.channeluser.channeluser.channelname,
        'image': 'http://localhost:8000'+sub.channeluser.channeluser.channelimg.url,
        'slug': sub.channeluser.channeluser.channelslug,
        'subs': len(sub.channeluser.channeluser.subscribers.all()),
    } for sub in subscribed_channels]

    playlists = [{
        'id': play.id,
        'playlistvisibility': play.playlist_visibility,
        'playlistuser': play.playlist_user.channeluser.channelname,
        'playlistname': play.playlist_name,
        'playlistvideos': list(play.playlist_videos.all().values()),
    } for play in plays]

    videos_data = [{
        'id': video.id,
        'title': video.title,
        'author': video.author.channeluser.channelname,
        'authorimg': 'http://localhost:8000'+video.author.channeluser.channelimg.url,
        'image': 'http://localhost:8000'+video.image.url,
        'duration': video.duration,
        'views': format_views_as_K(video.views),
        'published': time_ago(video.published),
        'description': video.description,
    } for video in videos]

    author_data = [{
        'username': user.id,
        'user': user.channeluser.username,
        'channelname': user.channelname,
        'channelbanner': 'http://localhost:8000'+user.banner.url,
        'channelslug': user.channelslug,
        'channelimg': 'http://localhost:8000'+user.channelimg.url,
        'subscribers': user.subscribers.all().count(),
        'videoslength': len(Video.objects.filter(author=user.channeluser).all()),
        'description': user.channeldescription,
        'joined': time_ago(user.joined),
        'user_liked': request.user in user.subscribers.all(),
        'joined': time_ago(user.joined),
        'totalviews': format_views_as_comma(totalviews),
    }]

    author_list = {
        'author_data': author_data,
        'videos_data': videos_data,
        'subscriber_channels': subscriber_channels,
        'playlists': playlists,
    }
    response = JsonResponse(author_list)
    response['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    return response


















def sub_videos(request):
    sub_channels = []
    sub_videos = []

    if request.user.is_authenticated:
        sub_channels = Channel.objects.filter(subscribers=request.user)
        sub_videos = Video.objects.filter(
            author__channeluser__in=sub_channels).all()

        video_list = []
        for video in sub_videos:
            video_dict = {
                'id': video.id,
                'title': video.title,
                'author': video.author.channeluser.channelname,
                'authorimg': 'http://localhost:8000'+video.author.channeluser.channelimg.url,
                'image': 'http://localhost:8000'+video.image.url,
                'duration': video.duration,
                'views': format_views_as_K(video.views),
                'published': time_ago(video.published),
            }
            video_list.append(video_dict)
        random.shuffle(video_list)
        response = JsonResponse(video_list, safe=False)
        response['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        return response
    else:
        return JsonResponse({'error': 'user is not authenticated'})


def liked_videos_api(request):
    if request.user.is_authenticated:
        videos = Video.objects.filter(liked=request.user).all().order_by('id')
        video_list = []
        for video in videos:
            video_dict = {
                'id': video.id,
                'title': video.title,
                'author': video.author.channeluser.channelname,
                'authorimg': 'http://localhost:8000'+video.author.channeluser.channelimg.url,
                'image': 'http://localhost:8000'+video.image.url,
                'duration': video.duration,
                'views': format_views_as_K(video.views),
                'published': time_ago(video.published),
            }
            video_list.append(video_dict)

        response = JsonResponse(video_list, safe=False)
        response['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        return response
    else:
        return JsonResponse({'error': 'error in fetching videos...'}, safe=False)


def user_videos(request):
    if request.user.is_authenticated:
        videos = Video.objects.filter(
            author=request.user).all().order_by('-published')
        video_list = []
        for video in videos:
            video_dict = {
                'id': video.id,
                'title': video.title,
                'author': video.author.channeluser.channelname,
                'authorimg': 'http://localhost:8000'+video.author.channeluser.channelimg.url,
                'image': 'http://localhost:8000'+video.image.url,
                'duration': video.duration,
                'views': format_views_as_K(video.views),
                'published': time_ago(video.published),
            }
            video_list.append(video_dict)

        response_data = {
            'videos': video_list,
            'videos_count': len(video_list)
        }
        response = JsonResponse(response_data, safe=False)
        response['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        return response
    else:
        return JsonResponse({'error': 'error in fetching user videos...'}, safe=False)

def featured_video(request):
    if request.user.is_authenticated:
        videos = Video.objects.filter(
            author=request.user).order_by('-views').first()
        video_list = []

        video_dict = {
            'id': videos.id,
            'title': videos.title,
            'author': videos.author.channeluser.channelname,
            'authorimg': 'http://localhost:8000'+videos.author.channeluser.channelimg.url,
            'image': 'http://localhost:8000'+videos.image.url,
            'duration': videos.duration,
            'views': format_views_as_K(videos.views),
            'video': 'http://localhost:8000/' + videos.video.url,
            'published': time_ago(videos.published),
        }
        video_list.append(video_dict)

        response = JsonResponse(video_list, safe=False)
        response['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        return response
    else:
        return JsonResponse({'error': 'error in fetching user videos...'}, safe=False)

def user_liked(request, id):
    user = request.user
    video = get_object_or_404(Video, id=id)

    if user in video.liked.all():
        return JsonResponse({'status': True}, safe=False)
    else:
        return JsonResponse({'status': False}, safe=False)

@csrf_exempt
def toggle_like(request, id):
    user = request.user
    video = get_object_or_404(Video, id=id)
    if request.user.is_authenticated:
        if user not in video.liked.all():
            video.liked.add(user)
            liked = True
        else:
            video.liked.remove(user)
            liked = False
        
        video.save()
        return JsonResponse({'liked': liked})
    else:
        return JsonResponse({'liked': 'user is not authenticated'}, safe=False)

@csrf_exempt
def toggle_subscribe(request, channelslug):
    subchannel = get_object_or_404(Channel, channelslug=channelslug)
    user = request.user
    if request.user.is_authenticated:
        if user not in subchannel.subscribers.all():
            subchannel.subscribers.add(user)
            subscribed = True
        else:
            subchannel.subscribers.remove(user)
            subscribed = False

        subchannel.save()
        return JsonResponse({'subscribed': subscribed})
    else:
        return JsonResponse({'error': 'user is not authenticated'}, safe=False)
        
def get_comments_json(request, id):
    try:
        video = Video.objects.get(id=id)
        comments = something.objects.filter(comment_video=video).all().order_by('-commented_on')
        serialized_comments = [{
            'id': comment.id,
            'comment_id': comment.comment_id,
            'commenter_image': 'http://localhost:8000'+comment.comment_user.channeluser.channelimg.url,
            'comment_author': comment.comment_user.channeluser.channelslug,
            'comment_user_id': comment.comment_user.channeluser.channelname,
            'comment_video_id': comment.comment_video.id,
            'comment_body': comment.comment_body,
            'commented_on': time_ago(comment.commented_on),
            'comment_liked': comment.comment_liked
        } for comment in comments]
        return JsonResponse(serialized_comments, safe=False)
    except Video.DoesNotExist:
        return JsonResponse({'error': 'comments for this video cannot be found'}, safe=False)



@csrf_exempt
def post_comment(request, id):
    video = get_object_or_404(Video, id=id)

    comments = something.objects.filter(comment_video=video)
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error in posting the comment'})
        
        form = CommentForm(data)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.comment_video = video
            # comment.comment_id = request.POST.get('comment_id')
            comment.comment_user = request.user if request.user.is_authenticated else None
            comment.comment_body = data.get('comment_body')
            comment.save()
            return JsonResponse({'status': 'comment posted successfully'})
        else:
            return JsonResponse({'status': 'error in posting the comment1'})
    else:
        form = CommentForm()


    print(list(comments.values()))
    
    return JsonResponse(list(comments.values()), safe=False)


def library_videos_json(request):
    user = request.user
    if request.user.is_authenticated:
        hisvideos = HistoryVideo.objects.filter(his_user=request.user).all().order_by('-his_time')
        watchvideos = Video.objects.filter(watchlater=user).all()
        likedvideos = Video.objects.filter(liked=request.user).all()
        playlists = Playlist.objects.filter(playlist_user=request.user).all()

        wviews = 0
        lviews = 0

        for i in watchvideos:
            wviews += i.views

        for j in likedvideos:
            lviews += j.views

        playlist_dict = [{
            'id': playlist.id,
            'name': playlist.playlist_name,
            'author': playlist.playlist_user.channeluser.channelname,
            'image': 'http://localhost:8000'+playlist.playlist_videos.first().image.url,
            'count': playlist.playlist_videos.all().count(),
            'visibility': playlist.playlist_visibility,
            'created': time_ago(playlist.playlist_created),
        } for playlist in playlists]

        liked_dict = [{
            'id': video.id,
            'title': video.title,
            'author': video.author.channeluser.channelname,
            'authorimg': 'http://localhost:8000'+video.author.channeluser.channelimg.url,
            'image': 'http://localhost:8000'+video.image.url,
            'duration': video.duration,
            'views': format_views_as_K(video.views),
            'published': time_ago(video.published),
        } for video in likedvideos]

        watchlater_dict = [{
            
            'id': video.id,
            'title': video.title,
            'author': video.author.channeluser.channelname,
            'image': 'http://localhost:8000'+video.image.url,
            'authorimg': 'http://localhost:8000'+video.author.channeluser.channelimg.url,
            'duration': video.duration,
            'views': format_views_as_K(video.views),
            'published': time_ago(video.published),
            'description': video.description,
        } for video in watchvideos]

        history_dict = [{
                'id': video.his_video.id,
                'title': video.his_video.title,
                'author': video.his_user.channeluser.channelname,
                'authorimg': 'http://localhost:8000'+video.his_user.channeluser.channelimg.url,
                'image': 'http://localhost:8000'+video.his_video.image.url,
                'duration': video.his_video.duration,
                'views': format_views_as_K(video.his_video.views),
                'published': time_ago(video.his_video.published),
                'description': video.his_video.description,
        } for video in hisvideos] 



        response_data = {
            'history': history_dict,
            'watchlater': watchlater_dict,
            'liked': liked_dict,
            'playlists': playlist_dict,
            'wviews': format_views_as_K(wviews),
            'lviews': format_views_as_K(lviews),
        }

        response = JsonResponse(response_data, safe=False)
        response['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        return response
    else:
        return JsonResponse({'error': 'error in fetching the response'})











def search_json(request):
    query = request.GET.get('query', '')
    result = Video.objects.filter(Q(title__icontains=query) | Q(description__icontains=query)).all()
    users = Channel.objects.filter(channelname__icontains=query).all()
    vids = ''
    for user in users:
        if user in Channel.objects.filter():
            vids = Video.objects.filter(author=user.channeluser)

    vids = [{
        'id': video.id,
        'title': video.title,
        'image': 'http://localhost:8000'+video.image.url,
        'author': video.author.channeluser.channelname,
        'views': format_views_as_K(video.views),
        'description': video.description,
        'published': time_ago(video.published),
    } for video in vids]

    users_list = [{
        'id': user.id,
        'channelname': user.channelname,
        'channelslug': user.channelslug,
        'channelimg': 'http://localhost:8000'+user.channelimg.url,
        'subscribers': user.subscribers.all().count(),
        'channeldescription': user.channeldescription,
        'vids': vids,
    } for user in users]

    serialized_results = [{
        'id': video.id,
        'title': video.title,
        'image': 'http://localhost:8000'+video.image.url,
        'author': video.author.channeluser.channelname,
        'views': format_views_as_K(video.views),
        'description': video.description,
        'published': time_ago(video.published),
    } for video in result]


    results = {
        'serialized_results': serialized_results,
        'users_list': users_list
    }

    return JsonResponse(results, safe=False)





@api_view(['GET'])
def apicomments(request, id):
    user = request.user
    video = get_object_or_404(Video, id=id)
    
    comments = something.objects.filter(comment_video=video).all().order_by('-commented_on')
    comment_dict = [{
        'comment_id': p.comment_id,
        'comment_user': p.comment_user.username,
        'commenter_image': 'http://localhost:8000'+p.comment_user.channeluser.channelimg.url,
        'comment_body': p.comment_body,
        'commented_on': time_ago(p.commented_on)
    } for p in comments]

    return JsonResponse(comment_dict, safe=False)



