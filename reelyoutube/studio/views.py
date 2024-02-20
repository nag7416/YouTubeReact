from django.shortcuts import render
from app.models import Video, Comment, something, Playlist
from django.http import HttpResponse, JsonResponse
import json
from django.db import models


def channel(request, id):
    videos = ''
    if request.user.is_authenticated:
        videos = Video.objects.filter(author=request.user).all().order_by('-published')
    count = {"values": []}
    for i in videos:
        comments = something.objects.filter(comment_video=i.id)
        count["values"].append(comments.count())

    json1 = json.dumps(count)

    print(request.path)
    context = {
        'id': request.path,
        'videos': videos,
        'comments': comments,
        'json1': json1,
    }
    return render(request, 'studio/studio_home.html', context)



def playlist(request, id):
    playlists = Playlist.objects.filter(playlist_user=request.user).all()
    playlistfirst = Playlist.objects.first()
    context = {
        'id': request.path,
        'playlists': playlists,
        'playlistfirst': playlistfirst
    }
    return render(request, 'studio/studio_playlists.html', context)


def comments(request, id):
    videos = Video.objects.filter(author=request.user).all()
    commen = {"values": []}
    for i in videos:
        comment = something.objects.filter(comment_video__exact=i.id)
        commen["values"].append(comment)
    print(commen)
    context = {
        'id': request.path,
        'comments': comments,
    }
    return render(request, 'studio/studio_comments.html', context)