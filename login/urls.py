from django.urls import path, include

from .views import *

app_name = 'login'
urlpatterns = [
    path('', index, name='index'),
    path('spotify_login', spotify_login, name='spotify_login'),
    path('callback', callback, name='callback'),
    #  path('user/<str:user_secret>', user_home, name='user_home'),
    path('admin_graphs', admin_graphs, name='admin_graphs'),
    path('upload_history', upload_history, name='upload_history'),
]
