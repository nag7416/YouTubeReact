from django.contrib import admin
from .models import Channel, Notification, Video, something, Playlist, HistoryVideo, Shorts

admin.site.register(Notification)
class VideoAdmin(admin.ModelAdmin):
    model = Video
    list_display = ['id', 'title', 'author', 'visibility', 'views']

admin.site.register(Video, VideoAdmin)


class ChannelAdmin(admin.ModelAdmin):
    model = Channel
    list_display = ['id', 'channelname', 'channeluser']
admin.site.register(Channel, ChannelAdmin)


class somethingAdmin(admin.ModelAdmin):
    model = something
    list_display = ['comment_id']
    list_filter = ['comment_user', 'comment_video']
admin.site.register(something, somethingAdmin)





class PlaylistAdmin(admin.ModelAdmin):
    model = Playlist
    list_display = ['playlist_name', 'playlist_user']
    list_filter = ['playlist_user']
admin.site.register(Playlist, PlaylistAdmin)





admin.site.register(HistoryVideo)
admin.site.register(Shorts)