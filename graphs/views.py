#  imports {{{ # 

import math
import random
import requests
import os
import urllib
import secrets
from pprint import pprint
import string
from datetime import datetime

from django.shortcuts import render, redirect
from .utils import *
from django_tables2 import RequestConfig, SingleTableView
from api.models import History

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

def display_history_table(request, user_secret):
    """Renders the user history page

    :param request: the HTTP request
    :param user_secret: user secret used for identification
    :return: renders the user history page
    """
    user_id = User.objects.get(secret=user_secret).id
    user_history = History.objects.filter(user__exact=user_id).order_by('-timestamp')
    history_table = HistoryTable(user_history)
    history_table.exclude = ('id', 'user', 'track', ) 
    RequestConfig(request).configure(history_table)

    context = { 'user_history_table': history_table, 
            'user_id': user_id, }

    return render(request, "graphs/user_history.html", context)

class HistoryList(SingleTableView):
    """Create table with list of song history."""
    model = History
    table_class = HistoryTable
    #  table_data =

