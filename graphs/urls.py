from django.urls import path, include

from .views import *

urlpatterns = [
    path('artists/<str:user_secret>', artist_data, 
        name='display_artist_graph'),
    path('genre/<str:user_secret>', display_genre_graph,
        name='display_genre_graph'),
    path('audio_features/<str:user_secret>', audio_features,
        name='display_audio_features'),
]
