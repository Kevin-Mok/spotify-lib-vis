#  imports {{{ # 
import requests
import math
import os
import json

from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Count, F, Max
from django.db.models import FloatField
from django.db.models.functions import Cast
from django.http import JsonResponse
from django.utils import timezone

from datetime import datetime
from dateutil.parser import parse
from pprint import pprint

from . import views
from .models import *
from login.models import User

HISTORY_ENDPOINT = 'https://api.spotify.com/v1/me/player/recently-played'

#  }}} imports # 

#  console_logging = True
console_logging = False
artists_genre_processed = 0
features_processed = 0

#  update_track_genres {{{ # 

def update_track_genres(user_obj):
    """Updates user_obj's tracks with the most common genre associated with the
    songs' artist(s).

    :user_obj: User object who's tracks are being updated.

    :returns: None

    """
    tracks_processed = 0
    user_tracks = Track.objects.filter(users__exact=user_obj)
    for track in user_tracks:
        # just using this variable to save another call to db
        track_artists = list(track.artists.all())
        # TODO: Use the most popular genre of the first artist as the Track genre
        first_artist_genres = track_artists[0].genres.all().order_by('-num_songs')

        undefined_genre_obj = Genre.objects.get(name="undefined")
        most_common_genre = first_artist_genres.first() if first_artist_genres.first() is \
                not undefined_genre_obj else first_artist_genres[1]
        track.genre = most_common_genre if most_common_genre is not None \
                else undefined_genre_obj
        track.save()
        tracks_processed += 1

        if console_logging:
            print("Added '{}' as genre for song #{} - '{}'".format(
                track.genre, 
                tracks_processed,
                track.name,
                ))

#  }}}  update_track_genres # 

#  save_track_obj {{{ # 

def save_track_obj(track_dict, artists, user_obj):
    """Make an entry in the database for this track if it doesn't exist already.

    :track_dict: dictionary from the API call containing track information.
    :artists: artists of the song, passed in as a list of Artist objects.
    :user_obj: User object for which this Track is to be associated with.

    :returns: (The created/retrieved Track object, created) 

    """
    track_query = Track.objects.filter(id__exact=track_dict['id'])
    if len(track_query) != 0:
        return track_query[0], False
    else:
        # check if track is simple or full, simple Track object won't have year
        #  if 'album' in track_dict:
        if 'release_date' in track_dict['album']:
        #  try:
            new_track = Track.objects.create(
                id=track_dict['id'],
                year=track_dict['album']['release_date'].split('-')[0],
                popularity=int(track_dict['popularity']),
                runtime=int(float(track_dict['duration_ms']) / 1000),
                name=track_dict['name'],
                )
        else:
        #  except (IntegrityError, KeyError) as e:
            new_track = Track.objects.create(
                id=track_dict['id'],
                popularity=int(track_dict['popularity']),
                runtime=int(float(track_dict['duration_ms']) / 1000),
                name=track_dict['name'],
                )

        # have to add artists and user_obj after saving object since track needs to
        # have ID before filling in m2m field
        for artist in artists:
            new_track.artists.add(artist)
            #  print(new_track.name, artist.name)
        if user_obj != None:
            new_track.users.add(user_obj)
        new_track.save()
        return new_track, True

#  }}} save_track_obj # 

#  get_audio_features {{{ # 

def get_audio_features(headers, track_objs):
    """Creates and saves a new AudioFeatures objects for the respective
    track_objs. track_objs should contain the API limit for a single call
    (FEATURES_LIMIT) for maximum efficiency.

    :headers: headers containing the API token
    :track_objs: Track objects to associate with the new AudioFeatures object
        
    :returns: None
    """
    track_ids = str.join(",", [track_obj.id for track_obj in track_objs])
    params = {'ids': track_ids}
    features_response = requests.get("https://api.spotify.com/v1/audio-features",
            headers=headers,
            params={'ids': track_ids}
            ).json()['audio_features']
    #  pprint.pprint(features_response)

    useless_keys = [ "key", "mode", "type", "liveness", "id", "uri",
            "track_href", "analysis_url", "time_signature", ]
    for i in range(len(track_objs)):
        if features_response[i] is not None:
            # Data that we don't need
            cur_features_obj = AudioFeatures()
            cur_features_obj.track = track_objs[i]
            for key, val in features_response[i].items():
                if key not in useless_keys:
                    setattr(cur_features_obj, key, val)
            cur_features_obj.save()

        if console_logging:
            global features_processed 
            features_processed += 1
            print("Added features for song #{} - {}".format(
                features_processed, track_objs[i].name))

#  }}} get_audio_features # 

#  process_artist_genre {{{ # 

def process_artist_genre(genre_name, artist_obj):
    """Increase count for corresponding Genre object to genre_name and associate that
    Genre object with artist_obj.

    :genre_name: Name of genre.
    :artist_obj: Artist object to associate Genre object with
    :returns: None

    """
    genre_obj, created = Genre.objects.get_or_create(name=genre_name, defaults={'num_songs': 1})
    if not created:
        genre_obj.num_songs = F('num_songs') + 1
        genre_obj.save()
    artist_obj.genres.add(genre_obj)
    artist_obj.save()

#  }}} process_artist_genre # 

#  add_artist_genres {{{ # 

def add_artist_genres(headers, artist_objs):
    """Adds genres to artist_objs and increases the count the respective Genre
    object. artist_objs should contain the API limit for a single call
    (ARTIST_LIMIT) for maximum efficiency.

    :headers: For making the API call.
    :artist_objs: List of Artist objects for which to add/tally up genres for.

    :returns: None

    """
    artist_ids = str.join(",", [artist_obj.id for artist_obj in artist_objs])
    artists_response = requests.get('https://api.spotify.com/v1/artists/',
            headers=headers,
            params={'ids': artist_ids},
            ).json()['artists']
    for i in range(len(artist_objs)):
        if len(artists_response[i]['genres']) == 0:
            process_artist_genre("undefined", artist_objs[i])
        else:
            for genre in artists_response[i]['genres']:
                process_artist_genre(genre, artist_objs[i])
                #  print(artist_objs[i].name, genre)

        if console_logging:
            global artists_genre_processed 
            artists_genre_processed += 1
            print("Added genres for artist #{} - {}".format(
                artists_genre_processed, artist_objs[i].name))

#  }}}  add_artist_genres # 

#  get_artists_in_genre {{{ # 

def get_artists_in_genre(user, genre):
    """Return count of artists in genre.

    :user: User object to return data for.
    :genre: genre to count artists for. (string)

    :returns: dict of artists in the genre along with the number of songs they
    have. 
    """
    genre_obj = Genre.objects.get(name=genre)
    tracks_in_genre = Track.objects.filter(genre=genre_obj, users=user)
    track_count = tracks_in_genre.count()
    user_artists = Artist.objects.filter(track__users=user)  # use this variable to save on db queries
    total_artist_counts = tracks_in_genre.aggregate(counts=Count('artists'))['counts']

    processed_artist_counts = {}
    for artist in user_artists:
        #  TODO: figure out collab problem # 
        #  artist_count = math.floor(artist.track_set.filter(genre=genre_obj,
            #  users=user).count() * track_count / total_artist_counts)
        artist_count = artist.track_set.filter(genre=genre_obj,
                users=user).count()
        if artist_count > 0:
            processed_artist_counts[artist.name] = artist_count
    return processed_artist_counts

#  }}} get_artists_in_genre # 

#  save_track_artists {{{ # 

def save_track_artists(track_dict, artist_genre_queue, user_headers):
    """ Update artist info before creating Track so that Track object can
    reference Artist object.

    :track_dict: response from Spotify API for track
    :returns: list of Artist objects in Track

    """
    track_artists = []
    for artist_dict in track_dict['artists']:
        try:
            artist_obj, artist_created = Artist.objects.get_or_create(
                    id=artist_dict['id'],
                    name=artist_dict['name'],)
            if artist_created:
                artist_genre_queue.append(artist_obj)
                if len(artist_genre_queue) == views.ARTIST_LIMIT:
                    add_artist_genres(user_headers, artist_genre_queue)
                    artist_genre_queue[:] = []
        #  artist changed name but same id
        except IntegrityError as e:
            artist_obj = Artist.objects.get(id=artist_dict['id'])
            artist_obj.name = artist_dict['name']
            artist_obj.save()
        # only add/tally up artist genres if new
        track_artists.append(artist_obj)

    return track_artists

#  }}} save_track_artists # 

#  get_user_header {{{ # 

def get_user_header(user_obj):
    """Returns the authorization string needed to make an API call.

    :user_obj: User to return the auth string for.
    :returns: the authorization string used for the header in a Spotify API
    call.

    """
    seconds_elapsed = (timezone.now() -
            user_obj.access_obtained_at).total_seconds()
    if seconds_elapsed >= user_obj.access_expires_in:
        req_body = {
            'grant_type': 'refresh_token',
            'refresh_token': user_obj.refresh_token,
            'client_id': os.environ['SPOTIFY_CLIENT_ID'],
            'client_secret': os.environ['SPOTIFY_CLIENT_SECRET']
        }
        
        token_response = requests.post('https://accounts.spotify.com/api/token',
                data=req_body).json()
        user_obj.access_token = token_response['access_token']
        user_obj.access_expires_in = token_response['expires_in']
        user_obj.save()

    return {'Authorization': "Bearer " + user_obj.access_token}

#  }}}  get_user_header # 

#  save_history_obj  {{{ # 

def save_history_obj (user, timestamp, track):
    """Return (get/create) a History object with the specified parameters. Can't
    use built-in get_or_create since don't know auto PK.

    :user: User object History should be associated with
    :timestamp: time at which song was listened to
    :track: Track object for song
    :returns: History object

    """
    history_query = History.objects.filter(user__exact=user,
            timestamp__exact=timestamp)
    if len(history_query) == 0:
        history_obj = History.objects.create(user=user, timestamp=timestamp,
                track=track)
    else:
        history_obj = history_query[0]

    return history_obj

#  }}} save_history_obj  # 

#  get_next_history_row {{{ # 

def get_next_history_row(csv_reader, headers, prev_info):
    """Return formatted information from next row in history CSV file.

    :csv_reader: TODO
    :headers: 
    :prev_info: history_obj_info of last row in case no more rows
    :returns: (boolean of if last row, dict with information of next row) 

    """
    try:
        row = next(csv_reader)
        #  if Track.objects.filter(id__exact=row[1]).exists():
        history_obj_info = {}
        for i in range(len(headers)):
            history_obj_info[headers[i]] = row[i]
        return False, history_obj_info
    except StopIteration:
        return True, prev_info

#  }}} get_next_history_row # 

#  parse_history {{{ # 

def parse_history(user_secret):
    """Scans user's listening history and stores the information in a
    database.

    :user_secret: secret for User object who's library is being scanned.
    :returns: None
    """

    user_obj = User.objects.get(secret=user_secret)
    payload = {'limit': str(views.USER_TRACKS_LIMIT)}
    last_time_played = History.objects.filter(user=user_obj).aggregate(Max('timestamp'))['timestamp__max']
    if last_time_played is not None:
        payload['after'] = last_time_played.isoformat()
    artist_genre_queue = []
    user_headers = get_user_header(user_obj)
    history_response = requests.get(HISTORY_ENDPOINT,
            headers=user_headers,
            params=payload).json()['items']
    #  pprint(history_response)

    tracks_processed = 0

    for track_dict in history_response:
        # don't associate history track with User, not necessarily in their
        # library
        #  track_obj, track_created = save_track_obj(track_dict['track'],
                #  track_artists, None)
        track_artists = save_track_artists(track_dict['track'], artist_genre_queue,
                user_headers)
        track_obj, track_created = save_track_obj(track_dict['track'],
                track_artists, None) 
        history_obj = save_history_obj(user_obj, parse(track_dict['played_at']),
                track_obj)
        tracks_processed += 1

        if console_logging:
            print("Added history track #{}: {}".format(
                tracks_processed, history_obj,))

    if len(artist_genre_queue) > 0:
        add_artist_genres(user_headers, artist_genre_queue)

    # TODO: update track genres from History relation
    #  update_track_genres(user_obj)

    print("Scanned {} history tracks for user {} at {}.".format(
        tracks_processed, user_obj.id, datetime.now()))

#  }}} get_history # 

