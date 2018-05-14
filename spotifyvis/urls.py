from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('callback', views.callback, name='callback'),
    path('user_data', views.user_data, name='user_data'),
]