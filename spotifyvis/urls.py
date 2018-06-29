from django.urls import path, include

from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('login', login, name='login'),
    path('callback', callback, name='callback'),
    path('user_data', user_data, name='user_data'),
    path('admin_graphs', admin_graphs, name='admin_graphs'),
    path('api/user_artists/<str:user_secret>', get_artist_data, name='get_artist_data'),
    path('graphs/artists/<str:user_secret>', artist_data, name='display_artist_graph'),
    path('api/user_genres/<str:user_secret>', get_genre_data, name='get_genre_data'),
    path('graphs/genre/<str:user_secret>', display_genre_graph,
         name='display_genre_graph'),
    path('graphs/audio_features/<str:user_secret>', audio_features, name='display_audio_features'),
    path('api/audio_features/<str:audio_feature>/<str:user_secret>',
         get_audio_feature_data, name='get_audio_feature_data'),
]
