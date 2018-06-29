from django.urls import path, include

from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('spotify_login', spotify_login, name='spotify_login'),
    path('callback', callback, name='callback'),
    path('user_data', user_data, name='user_data'),
    path('admin_graphs', admin_graphs, name='admin_graphs'),
]
