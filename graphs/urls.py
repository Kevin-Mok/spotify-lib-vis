from django.urls import path, include

from .views import *

app_name = 'graphs'
urlpatterns = [
    path('artists/<str:user_secret>', display_artist_graph, 
        name='display_artist_graph'),
    path('genre/<str:user_secret>', display_genre_graph,
        name='display_genre_graph'),
    path('audio_features/<str:user_secret>', display_features_graphs,
        name='display_audio_features'),
    path('history/<str:user_secret>', display_history_table,
        name='display_history_table'),
]
