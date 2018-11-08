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
from django_tables2.export.views import ExportMixin
from django_tables2.export import TableExport
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

#  HistoryList {{{ # 

class HistoryList(ExportMixin, SingleTableView):
    """Create table with list of song history."""
    model = History
    table_class = HistoryTable
    context_table_name = 'user_history_table'
    template_name = 'graphs/user_history.html'

    #  overridden methods {{{ # 
    
    def get_table_kwargs(self):
        return { 'exclude': ('id', 'user', 'track', 'track_id', 'iso_timestamp', ) }

    def get_table_data(self):
        return History.objects.filter(user__exact=self.request.session['user_id']).order_by('-timestamp')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_id'] = self.request.session['user_id']
        context['total_history'] = self.get_table_data().count()
        return context

    def get_export_filename(self, export_format):
        return "{}.{}".format(self.request.session['user_id'], export_format)

    def create_export(self, export_format):
        export_exclude = ('id', 'user', 'track', 'track_name', 'artists',
                'timestamp', )
        exporter = TableExport(
            export_format=export_format,
            table=self.get_table(exclude=export_exclude),
            exclude_columns=self.exclude_columns,
        )

        return exporter.response(filename=self.get_export_filename(export_format))
    
    #  }}} overridden methods # 

#  }}} HistoryList # 

