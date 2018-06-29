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
from .utils import get_artists_in_genre, update_track_genres
from .models import User, Track, AudioFeatures, Artist 

#  }}} imports # 

TRACKS_TO_QUERY = 200

#  parse_library {{{ # 

def parse_library(headers, tracks, user):
    """Scans user's library for certain number of tracks and store the information in a database

    :headers: For API call.
    :tracks: Number of tracks to get from user's library.
    :user: a User object representing the user whose library we are parsing

    :returns: None

    """
    #  TODO: implement importing entire library with 0 as tracks param
    # keeps track of point to get songs from
    offset = 0
    payload = {'limit': str(USER_TRACKS_LIMIT)}
    artist_genre_queue = []
    features_queue = []

    # iterate until hit requested num of tracks
    for i in range(0, tracks, USER_TRACKS_LIMIT):
        payload['offset'] = str(offset)
        saved_tracks_response = requests.get('https://api.spotify.com/v1/me/tracks', 
                headers=headers,
                params=payload).json()

        for track_dict in saved_tracks_response['items']:
            #  add artists {{{ # 
            
            # update artist info before track so that Track object can reference
            # Artist object
            track_artists = []
            for artist_dict in track_dict['track']['artists']:
                artist_obj, artist_created = Artist.objects.get_or_create(
                        artist_id=artist_dict['id'],
                        name=artist_dict['name'],)
                # only add/tally up artist genres if new
                if artist_created:
                    artist_genre_queue.append(artist_obj)
                    if len(artist_genre_queue) == ARTIST_LIMIT:
                        add_artist_genres(headers, artist_genre_queue)
                        artist_genre_queue = []
                track_artists.append(artist_obj)
            
            #  }}} add artists # 
            
            # TODO: fix this, don't need any more
            top_genre = ""
            track_obj, track_created = save_track_obj(track_dict['track'], 
                    track_artists, top_genre, user)

            #  add audio features {{{ # 
            
            # if a new track is not created, the associated audio feature does
            # not need to be created again
            if track_created:
                features_queue.append(track_obj)
                if len(features_queue) == FEATURES_LIMIT:
                    get_audio_features(headers, features_queue)
                    features_queue = []
            
            #  }}} add audio features # 

            # temporary console logging
            print("#{}-{}: {} - {}".format(offset + 1,
                offset + USER_TRACKS_LIMIT, 
                track_obj.artists.first(), 
                track_obj.name))

        # calculates num_songs with offset + songs retrieved
        offset += USER_TRACKS_LIMIT

    #  clean-up {{{ # 
    
    # update remaining artists without genres and songs without features if
    # there are any
    if len(artist_genre_queue) > 0:
        add_artist_genres(headers, artist_genre_queue)
    if len(features_queue) > 0:
        get_audio_features(headers, features_queue)
    
    #  }}} clean-up # 

    update_track_genres(user)

#  }}} parse_library # 

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
