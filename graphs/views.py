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
from .utils import *

#  }}} imports # 

def display_artist_graph(request, user_secret):
    """Renders the artist data graph display page

    :param request: the HTTP request
    :param user_secret: the user secret used for identification
    :return: render the artist data graph display page
    """
    return render(request, "graphs/artist_graph.html", 
            get_secret_context(user_secret))


def display_genre_graph(request, user_secret):
    return render(request, "graphs/genre_graph.html",
            get_secret_context(user_secret))


def display_features_graphs(request, user_secret):
    """Renders the audio features page

    :param request: the HTTP request
    :param user_secret: user secret used for identification
    :return: renders the audio features page
    """
    return render(request, "graphs/features_graphs.html",
            get_secret_context(user_secret))
