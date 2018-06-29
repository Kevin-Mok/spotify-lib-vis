#  imports {{{ # 

import math
import random
import requests
import os
import urllib
import secrets
import pprint
import string
from datetime import datetime

from django.shortcuts import render, redirect

#  }}} imports # 

def artist_data(request, user_secret):
    """Renders the artist data graph display page

    :param request: the HTTP request
    :param user_secret: the user secret used for identification
    :return: render the artist data graph display page
    """
    user = User.objects.get(user_secret=user_secret)
    context = {
        'user_id': user.user_id,
        'user_secret': user_secret,
    }
    return render(request, "spotifyvis/artist_graph.html", context)

def display_genre_graph(request, user_secret):
    user = User.objects.get(user_secret=user_secret)
    context = {
        'user_secret': user_secret,
    }
    return render(request, "spotifyvis/genre_graph.html", context)


def audio_features(request, user_secret):
    """Renders the audio features page

    :param request: the HTTP request
    :param user_secret: user secret used for identification
    :return: renders the audio features page
    """
    user = User.objects.get(user_secret=user_secret)
    context = {
        'user_id': user.user_id,
        'user_secret': user_secret,
    }
    return render(request, "spotifyvis/audio_features.html", context)
