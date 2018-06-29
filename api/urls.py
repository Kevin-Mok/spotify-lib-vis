from django.urls import path, include

from .views import *

app_name = 'api'
urlpatterns = [
    path('scan/<str:user_secret>', parse_library,
        name='scan'),
    path('user_artists/<str:user_secret>', get_artist_data,
        name='get_artist_data'),
    path('user_genres/<str:user_secret>', get_genre_data,
        name='get_genre_data'),
    path('audio_features/<str:audio_feature>/<str:user_secret>',
        get_audio_feature_data, name='get_audio_feature_data'),
]
