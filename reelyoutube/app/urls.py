from django.urls import path
from .views import shorts, author_channel_videos, channel, channel_videos, channel_about,explore, home, library, like, login, notifications, search, subscribe, subscriptions, unlike, unsubscribe, watch, author_channel, history, LikeNotification, liked_videos, watchlater_videos, author_channel_about, watchsubscribe, watchunsubscribe, channel_playlists, author_channel_playlists, channel_channels, author_channel_channels, like_comment, unlike_comment, APIView, VideoView, UserView, delete_comment, get_comments, ReactView, load_articles, nointernet, video_title_suggestions, explore_videos, get_video, get_user_data, sub_videos, liked_videos_api, user_videos, featured_video, user_liked, toggle_like, get_comments_json, toggle_subscribe, post_comment, library_videos_json, search_json, author_channel_json, user_channel_json, videosapi, apicomments

urlpatterns = [
    path('', home, name=''),
    path('feed/shorts', shorts, name='shorts'),
    path('video-title-suggestions/', video_title_suggestions, name='video_title_suggestions'),

    path('api/<str:id>/get_comments_json', get_comments_json, name='get_comments_json'),

    path('api', ReactView.as_view(), name='api'),

    path('api/videos', videosapi, name='videosapi'),

    path('api/get_video/<str:id>', get_video, name='get_video'),
    path('api/sub_videos', sub_videos, name='sub_videos'),
    path('api/get_user_data', get_user_data, name='get_user_data'),
    path('api/explore', explore_videos, name='explore_videos'),
    path('api/liked_videos_api', liked_videos_api, name='liked_videos_api'),
    path('api/user_videos', user_videos, name='user_videos'),
    path('api/featured_video', featured_video, name='featured_video'),
    path('api/library_videos_json', library_videos_json, name='library_videos_json'),
    path('api/user_liked/<str:id>', user_liked, name='user_liked'),
    path('api/<str:id>/toggle_like', toggle_like, name='toggle_like'),

    path('api/<str:id>/post_comment', post_comment, name='post_comment'),
    path('api/<str:id>/comments', apicomments, name='apicomments'),

    path('api/<str:channelslug>/toggle_subscribe', toggle_subscribe, name='toggle_subscribe'),

    path('api/search', search_json, name='search_json'),

    path('api/<str:channelslug>', author_channel_json, name='author_channel_json'),

    path('api/user_channel_json/<str:channelslug>', user_channel_json, name='user_channel_json'),



    path('userapi', UserView.as_view(), name='userapi'),
    path('api/<str:id>', VideoView.as_view(), name='videoview'),
    path('login', login, name='login'),
    path('watch/<str:id>', watch, name='watch'),

    path('watch/<str:id>/comments', get_comments, name='get_comments'),

    path('watch/<str:id>/<str:comment_id>/like', like_comment, name='like_comment'),
    path('watch/<str:id>/<str:comment_id>/unlike', unlike_comment, name='unlike_comment'),

    path('watch/<str:id>/<str:comment_id>/delete', delete_comment, name='delete_comment'),

    path('feed/explore', explore, name='explore'),
    path('feed/history', history, name='history'),
    path('feed/library', library, name='library'),
    path('feed/subscriptions', subscriptions, name='subscriptions'),
    path('search', search, name='search'),
    path('notifications', notifications, name='notifications'),

    path('playlist', liked_videos, name='liked_videos'),
    path('wplaylist', watchlater_videos, name='watchlater_videos'),

    path('watch/<str:id>/like', like, name='like'),
    path('watch/<str:id>/unlike', unlike, name='unlike'),
    path('watch/<str:id>/<str:channelname>/subscribe', watchsubscribe, name='watchsubscribe'),
    path('watch/<str:id>/<str:channelname>/unsubscribe', watchunsubscribe, name='watchunsubscribe'),


    path('channel/<str:id>', channel, name='channel'),
    path('channel/<str:id>/videos', channel_videos, name='channel_videos'),
    path('channel/<str:id>/playlists', channel_playlists, name='channel_playlists'),
    path('channel/<str:id>/about', channel_about, name='channel_about'),
    path('channel/<str:id>/channels', channel_channels, name='channel_channels'),



    path('@<str:channelslug>', author_channel, name='author_channel'),
    path('@<str:channelslug>/videos', author_channel_videos, name='author_channel_videos'),
    path('@<str:channelslug>/about', author_channel_about, name='author_channel_about'),
    path('@<str:channelslug>/playlists', author_channel_playlists, name='author_channel_playlists'),
    path('@<str:channelslug>/channels', author_channel_channels, name='author_channel_channels'),


    path('c/<str:channelslug>/subscribe', subscribe, name='subscribe'),
    path('c/<str:channelslug>/unsubscribe', unsubscribe, name='unsubscribe'),


    path('load_articles/', load_articles, name='load_articles'),
    path('offline/', nointernet, name='nointernet'),

]
