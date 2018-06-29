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

from django.http import JsonResponse
from django.db.models import Count, Q
from .utils import parse_library, get_artists_in_genre, update_track_genres
from .models import User, Track, AudioFeatures, Artist 

#  }}} imports # 

TRACKS_TO_QUERY = 200

#  get_artist_data {{{ # 


def get_artist_data(request, user_secret):
    """Returns artist data as a JSON serialized list of dictionaries
    The (key, value) pairs are (artist name, song count for said artist)

    :param request: the HTTP request
    :param user_secret: the user secret used for identification
    :return: a JsonResponse
    """
    user = User.objects.get(user_secret=user_secret)
    artist_counts = Artist.objects.annotate(num_songs=Count('track',
                                            filter=Q(track__users=user)))
    processed_artist_counts = [{'name': artist.name,
                                'num_songs': artist.num_songs} for artist in artist_counts]
    return JsonResponse(data=processed_artist_counts, safe=False) 

#  }}} get_artist_data # 

#  get_audio_feature_data {{{ # 

def get_audio_feature_data(request, audio_feature, user_secret):
    """Returns all data points for a given audio feature

    Args:
        request: the HTTP request
        audio_feature: The audio feature to be queried
        user_secret: client secret, used to identify the user
    """
    user = User.objects.get(user_secret=user_secret)
    user_tracks = Track.objects.filter(users=user)
    response_payload = {
        'data_points': [],
    }
    for track in user_tracks:
        try:
            audio_feature_obj = AudioFeatures.objects.get(track=track)
            response_payload['data_points'].append(getattr(audio_feature_obj, audio_feature))
        except AudioFeatures.DoesNotExist:
            continue
    return JsonResponse(response_payload)

#  }}} get_audio_feature_data # 

#  get_genre_data {{{ # 

def get_genre_data(request, user_secret):
    """Return genre data needed to create the graph user.
    TODO
    """
    user = User.objects.get(user_secret=user_secret)
    genre_counts = (Track.objects.filter(users__exact=user)
            .values('genre')
            .order_by('genre')
            .annotate(num_songs=Count('genre'))
            )
    for genre_dict in genre_counts:
        genre_dict['artists'] = get_artists_in_genre(user, genre_dict['genre'],
                genre_dict['num_songs'])
    print("*** Genre Breakdown ***")
    pprint.pprint(list(genre_counts))
    return JsonResponse(data=list(genre_counts), safe=False) 

#  }}} get_genre_data  # 
