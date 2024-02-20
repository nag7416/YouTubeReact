from django.urls import path
from .views import channel, playlist, comments

urlpatterns = [
    path('channel/<str:id>/videos', channel, name='studio'),
    path('channel/<str:id>/playlists', playlist, name='playlist'),
    path('channel/<str:id>/comments', comments, name='comments'),
]
