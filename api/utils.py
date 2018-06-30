#  imports {{{ # 
import requests
import math
import pprint
import os
import json

from django.db.models import Count, Q, F
from django.http import JsonResponse
from django.core import serializers
from django.utils import timezone
from .models import *
from login.models import User

#  }}} imports # 

console_logging = True
#  console_logging = False
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
        track_artists = track.artists.all()
        # set genres to first artist's genres then find intersection with others
        shared_genres = track_artists.first().genres.all()
        for artist in track_artists:
            shared_genres = shared_genres.intersection(artist.genres.all())
        shared_genres = shared_genres.order_by('-num_songs')

        undefined_genre_obj = Genre.objects.get(name="undefined")
        most_common_genre = shared_genres.first() if shared_genres.first() is \
                not undefined_genre_obj else shared_genres[1]
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
        new_track = Track.objects.create(
            id=track_dict['id'],
            year=track_dict['album']['release_date'].split('-')[0],
            popularity=int(track_dict['popularity']),
            runtime=int(float(track_dict['duration_ms']) / 1000),
            name=track_dict['name'],
            )

        # have to add artists and user_obj after saving object since track needs to
        # have ID before filling in m2m field
        for artist in artists:
            new_track.artists.add(artist)
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
    """Increase count for correspoding Genre object to genre_name and add that
    Genre to artist_obj. 

    :genre_name: Name of genre.
    :artist_obj: Artist object to add Genre object to.
    :returns: None

    """
    genre_obj, created = Genre.objects.get_or_create(name=genre_name,
            defaults={'num_songs':1})
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
    params = {'ids': artist_ids}
    artists_response = requests.get('https://api.spotify.com/v1/artists/',
            headers=headers, 
            params=params,
            ).json()['artists']
    for i in range(len(artist_objs)):
        if len(artists_response[i]['genres']) == 0:
            process_artist_genre("undefined", artist_objs[i])
        else:
            for genre in artists_response[i]['genres']:
                process_artist_genre(genre, artist_objs[i])

        if console_logging:
            global artists_genre_processed 
            artists_genre_processed += 1
            print("Added genres for artist #{} - {}".format(
                artists_genre_processed, artist_objs[i].name))

#  }}}  add_artist_genres # 

#  get_artists_in_genre {{{ # 

def get_artists_in_genre(user, genre, max_songs):
    """Return count of artists in genre.

    :user: User object to return data for.
    :genre: genre to count artists for.
    :max_songs: max total songs to include to prevent overflow due to having
    multiple artists on each track.

    :returns: dict of artists in the genre along with the number of songs they
    have. 
    """
    genre_obj = Genre.objects.get(name=genre)
    artist_counts = (Artist.objects.filter(track__users=user)
            .filter(genres=genre_obj) 
            .annotate(num_songs=Count('track', distinct=True))
            .order_by('-num_songs')
            )
    processed_artist_counts = {}
    songs_added = 0
    for artist in artist_counts:
        # hacky way to not have total count overflow due to there being multiple
        # artists on a track
        if songs_added + artist.num_songs <= max_songs:
            processed_artist_counts[artist.name] = artist.num_songs
            songs_added += artist.num_songs
    #  processed_artist_counts = [{'name': artist.name, 'num_songs': artist.num_songs} for artist in artist_counts]
    #  processed_artist_counts = {artist.name: artist.num_songs for artist in artist_counts}
    #  pprint.pprint(processed_artist_counts)
    return processed_artist_counts

#  }}} get_artists_in_genre # 

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
