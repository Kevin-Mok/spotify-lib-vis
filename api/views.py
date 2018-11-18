#  imports {{{ # 

import math
import random
import requests
import urllib
import secrets
import string
import csv

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Count, Q, Max
from django.core.files import File
from .utils import *
from .models import *
from login.models import User
from login.utils import get_user_context
from dateutil.parser import parse
from pprint import pprint
from login.models import HistoryUpload

#  }}} imports # 

#  constants {{{ # 

USER_TRACKS_LIMIT = 50
TRACKS_LIMIT = 50
HISTORY_LIMIT = 50
ARTIST_LIMIT = 50
FEATURES_LIMIT = 100
#  ARTIST_LIMIT = 25
#  FEATURES_LIMIT = 25
TRACKS_TO_QUERY = 100
TRACKS_ENDPOINT = 'https://api.spotify.com/v1/tracks'

console_logging = True
#  console_logging = False

#  }}} constants # 

#  parse_library {{{ # 

def parse_library(request, user_secret):
    """Scans user's library for num_tracks and store the information in a
    database.

    :user_secret: secret for User object who's library is being scanned.
    :returns: None
    """

    offset = 0
    payload = {'limit': str(USER_TRACKS_LIMIT)}
    artist_genre_queue = []
    features_queue = []
    user_obj = User.objects.get(secret=user_secret)
    user_headers = get_user_header(user_obj)

    # create this obj so loop runs at least once
    saved_tracks_response = [0]
    # scan until reach num_tracks or no tracks left if scanning entire library
    while ((TRACKS_TO_QUERY == 0 or offset < TRACKS_TO_QUERY) and
            len(saved_tracks_response) > 0):
        payload['offset'] = str(offset)
        saved_tracks_response = requests.get('https://api.spotify.com/v1/me/tracks', 
                headers=user_headers,
                params=payload).json()['items']

        if console_logging:
            tracks_processed = 0

        for track_dict in saved_tracks_response:
            track_artists = save_track_artists(track_dict['track'], artist_genre_queue,
                    user_headers)
            track_obj, track_created = save_track_obj(track_dict['track'], 
                    track_artists, user_obj)

            #  add audio features {{{ # 
            
            # if a new track is not created, the associated audio feature does
            # not need to be created again
            if track_created:
                features_queue.append(track_obj)
                if len(features_queue) == FEATURES_LIMIT:
                    get_audio_features(user_headers, features_queue)
                    features_queue = []
            
            #  }}} add audio features # 

            if console_logging:
                tracks_processed += 1
                print("Added track #{}: {} - {}".format(
                    offset + tracks_processed,
                    track_obj.artists.first(), 
                    track_obj.name,
                    ))

        # calculates num_songs with offset + songs retrieved
        offset += USER_TRACKS_LIMIT

    #  clean-up {{{ # 
    
    # update remaining artists without genres and songs without features if
    # there are any
    if len(artist_genre_queue) > 0:
        add_artist_genres(user_headers, artist_genre_queue)
    if len(features_queue) > 0:
        get_audio_features(user_headers, features_queue)
    
    #  }}} clean-up # 

    update_track_genres(user_obj)

    return render(request, 'graphs/logged_in.html', get_user_context(user_obj))

#  }}} parse_library # 

#  parse_history_request {{{ # 

def parse_history_request(request, user_secret):
    """Request function to call parse_history. Scans user's listening history
    and stores the information in a database.

    :user_secret: secret for User object who's library is being scanned.
    :returns: redirects user to logged in page
    """
    parse_history(user_secret)
    return render(request, 'graphs/logged_in.html',
            get_user_context(User.objects.get(secret=user_secret)))

#  }}} get_history # 

#  get_artist_data {{{ # 

def get_artist_data(request, user_secret):
    """Returns artist data as a JSON serialized list of dictionaries
    The (key, value) pairs are (artist name, song count for said artist)

    :param request: the HTTP request
    :param user_secret: the user secret used for identification
    :return: a JsonResponse
    """
    user = User.objects.get(secret=user_secret)
    artist_counts = Artist.objects.annotate(num_songs=Count('track',
        filter=Q(track__users=user)))
    processed_artist_counts = [{'name': artist.name, 'num_songs': artist.num_songs} 
            for artist in artist_counts]
    pprint(processed_artist_counts)
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
    user = User.objects.get(secret=user_secret)
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
    user = User.objects.get(secret=user_secret)
    genre_counts = (Track.objects.filter(users__exact=user)
            .values('genre')
            .order_by('genre')
            .annotate(num_songs=Count('genre'))
            )
    for genre_dict in genre_counts:
        genre_dict['artists'] = get_artists_in_genre(user, genre_dict['genre'],
                genre_dict['num_songs'])
    print("*** Genre Breakdown ***")
    pprint(list(genre_counts))
    return JsonResponse(data=list(genre_counts), safe=False) 

#  }}} get_genre_data  # 

#  import_history {{{ # 

def import_history(request, upload_id):
    """Import history for the user from the file they uploaded.

    :upload_id: ID (PK) of the HistoryUpload entry
    :returns: None
    """

    #  setup {{{ # 
    
    headers = ['timestamp', 'track_id']
    upload_obj = HistoryUpload.objects.get(id=upload_id)
    user_headers = get_user_header(upload_obj.user)

    with upload_obj.document.open('r') as f:
        csv_reader = csv.reader(f, delimiter=',')
        rows_read = 0
        history_obj_info_lst = []
        artist_genre_queue = []

        # skip header row
        last_row, history_obj_info = get_next_history_row(csv_reader, headers,
                {})
        while not last_row:
            last_row, history_obj_info = get_next_history_row(csv_reader,
                    headers, history_obj_info)

    #  }}} setup # 

            history_obj_info_lst.append(history_obj_info)
            # PU: refactor saving History object right away if Track obj already
            # exists
            # PU: refactor below?
            rows_read += 1
            if (rows_read % TRACKS_LIMIT == 0) or last_row:
                #  get tracks_response {{{ # 
                
                track_ids_lst = [info['track_id'] for info in history_obj_info_lst]
                #  print(len(track_ids_lst))
                track_ids = ','.join(track_ids_lst)
                payload = {'ids': track_ids}
                tracks_response = requests.get(TRACKS_ENDPOINT,
                        headers=user_headers,
                        params=payload).json()['tracks']
                responses_processed = 0
                
                #  }}} get tracks_response # 

                for track_dict in tracks_response:
                    # don't associate history track with User, not necessarily in their
                    # library
                    track_artists = save_track_artists(track_dict, artist_genre_queue,
                            user_headers)
                    track_obj, track_created = save_track_obj(track_dict,
                            track_artists, None)

                    timestamp = \
                        parse(history_obj_info_lst[responses_processed]['timestamp'])
                    history_obj = save_history_obj(upload_obj.user, timestamp,
                            track_obj)

                    if console_logging:
                        print("Processed row #{}: {}".format(
                            (rows_read - TRACKS_LIMIT) + responses_processed, history_obj,))
                        responses_processed += 1

                history_obj_info_lst = []

                if len(artist_genre_queue) > 0:
                    add_artist_genres(user_headers, artist_genre_queue)

                # TODO: update track genres from History relation
                #  update_track_genres(user_obj)

    return redirect('graphs:display_history_table')

#  }}} get_history # 

