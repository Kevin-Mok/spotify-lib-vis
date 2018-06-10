from django.urls import path, include
from django.conf.urls import url

from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('login', login, name='login'),
    path('callback', callback, name='callback'),
    path('user_data', user_data, name='user_data'),
    path('test_db', test_db, name='test_db'),
    path('user_artists/<str:user_id>', get_artist_data, name='get_artist_data'),
    path('audio_features/<str:audio_feature>/<str:client_secret>', get_audio_feature_data, name='get_audio_feature_data'),

]
