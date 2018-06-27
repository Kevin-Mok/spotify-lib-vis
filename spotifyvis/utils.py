#  imports {{{ # 
import requests
import math
import pprint

from .models import *
from django.db.models import Count, Q, F
from django.http import JsonResponse
from django.core import serializers
import json

#  }}} imports # 

USER_TRACKS_LIMIT = 50
#  ARTIST_LIMIT = 50
ARTIST_LIMIT = 25
#  FEATURES_LIMIT = 100
FEATURES_LIMIT = 25

#  parse_library {{{ # 

def parse_library(headers, tracks, user):
    """Scans user's library for certain number of tracks to update library_stats with.

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
    for _ in range(0, tracks, USER_TRACKS_LIMIT):
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
            
            # WIP: get most common genre
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

#  update_track_genres {{{ # 

def update_track_genres(user):
    """Updates user's tracks with the most common genre associated with the
    songs' artist(s).

    :user: User object who's tracks are being updated.

    :returns: None

    """
    user_tracks = Track.objects.filter(users__exact=user)
    for track in user_tracks:
        track_artists = list(track.artists.all())
        if len(track_artists) == 1:
            track.genre = track_artists[0].genres.all().order_by('-num_songs').first()
            track.save()
            #  print(track_artists, track.genre)

#  }}}  update_track_genres # 

#  save_track_obj {{{ # 

def save_track_obj(track_dict, artists, top_genre, user):
    """Make an entry in the database for this track if it doesn't exist already.

    :track_dict: dictionary from the API call containing track information.
    :artists: artists of the song, passed in as a list of Artist objects.
    :top_genre: top genre associated with this track (see get_top_genre).
    :user: User object for which this Track is to be associated with.

    :returns: (The created/retrieved Track object, created) 

    """
    track_query = Track.objects.filter(track_id__exact=track_dict['id'])
    if len(track_query) != 0:
        return track_query[0], False
    else:
        new_track = Track.objects.create(
            track_id=track_dict['id'],
            year=track_dict['album']['release_date'].split('-')[0],
            popularity=int(track_dict['popularity']),
            runtime=int(float(track_dict['duration_ms']) / 1000),
            name=track_dict['name'],
            #  genre=top_genre,
            )

        # have to add artists and user after saving object since track needs to
        # have ID before filling in m2m field
        for artist in artists:
            new_track.artists.add(artist)
        new_track.users.add(user)
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
    track_ids = str.join(",", [track_obj.track_id for track_obj in track_objs])
    params = {'ids': track_ids}
    features_response = requests.get("https://api.spotify.com/v1/audio-features",
            headers=headers,params=params).json()['audio_features']
    #  pprint.pprint(features_response)

    useless_keys = [ "key", "mode", "type", "liveness", "id", "uri", "track_href", "analysis_url", "time_signature", ]
    for i in range(len(track_objs)):
        if features_response[i] is not None:
            # Data that we don't need
            cur_features_obj = AudioFeatures()
            cur_features_obj.track = track_objs[i]
            for key, val in features_response[i].items():
                if key not in useless_keys:
                    setattr(cur_features_obj, key, val)
            cur_features_obj.save()

#  }}} get_audio_features # 

# WIP: is this being removed to redo genre data?
def get_top_genre(headers, top_artist_id):
    """Updates the top genre for a track by querying the Spotify API

    :headers: For making the API call.
    :top_artist: The first artist's (listed in the track) Spotify ID.

    :returns: The first genre listed for the top_artist.

    """
    artist_response = requests.get('https://api.spotify.com/v1/artists/' +
            top_artist_id, headers=headers).json()
    #  pprint.pprint(artist_response)
    if len(artist_response['genres']) > 0:
        return artist_response['genres'][0]
    else:
        return "undefined"

#  add_artist_genres {{{ # 

def add_artist_genres(headers, artist_objs):
    """Adds genres to artist_objs and increases the count the respective Genre
    object. artist_objs should contain the API limit for a single call
    (ARTIST_LIMIT) for maximum efficiency.

    :headers: For making the API call.
    :artist_objs: List of Artist objects for which to add/tally up genres for.

    :returns: None

    """
    artist_ids = str.join(",", [artist_obj.artist_id for artist_obj in artist_objs])
    params = {'ids': artist_ids}
    artists_response = requests.get('https://api.spotify.com/v1/artists/',
            headers=headers, params=params).json()['artists']
    #  pprint.pprint(artists_response)
    for i in range(len(artist_objs)):
        for genre in artists_response[i]['genres']:
            genre_obj, created = Genre.objects.get_or_create(name=genre,
                    defaults={'num_songs':1})
            if not created:
                genre_obj.num_songs = F('num_songs') +1
                genre_obj.save()
            artist_objs[i].genres.add(genre_obj)
            artist_objs[i].save()

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
    artist_counts = (Artist.objects.filter(track__users=user)
            .filter(track__genre=genre) 
            .annotate(num_songs=Count('track', distinct=True))
            .order_by('-num_songs')
            )
    processed_artist_counts = {}
    songs_added = 0
    for artist in artist_counts:
        if songs_added + artist.num_songs <= max_songs:
            processed_artist_counts[artist.name] = artist.num_songs
            songs_added += artist.num_songs
    #  processed_artist_counts = [{'name': artist.name, 'num_songs': artist.num_songs} for artist in artist_counts]
    #  processed_artist_counts = {artist.name: artist.num_songs for artist in artist_counts}
    #  pprint.pprint(processed_artist_counts)
    return processed_artist_counts

#  }}} get_artists_in_genre # 
