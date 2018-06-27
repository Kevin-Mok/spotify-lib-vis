from django.urls import path, include
from django.conf.urls import url

from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('login', login, name='login'),
    path('callback', callback, name='callback'),
    path('user_data', user_data, name='user_data'),
    path('admin_graphs', admin_graphs, name='admin_graphs'),
    path('user_artists/<str:user_id>', get_artist_data, name='get_artist_data'),
    path('api/user_genres/<str:user_secret>', get_genre_data, name='get_genre_data'),
    path('graphs/genre/<str:client_secret>', display_genre_graph,
        name='display_genre_graph'),
    path('audio_features/<str:client_secret>', audio_features, name='audio_features'),
    path('audio_features/<str:audio_feature>/<str:client_secret>',
        get_audio_feature_data, name='get_audio_feature_data'),
]
