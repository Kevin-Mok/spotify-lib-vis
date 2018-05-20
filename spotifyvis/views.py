from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest
import math
import random
import requests
import os
import urllib
import json
import pprint
from datetime import datetime

TIME_FORMAT = '%Y-%m-%d-%H-%M-%S'
library_stats = {"audio_features":{}, "genres":{}, "year_released":{}, "artists":{}, "num_songs":0, "popularity":[], "total_runtime":0}

#  generate_random_string {{{ # 

def generate_random_string(length):
    """Generates a random string of a certain length

    Args:
        length: the desired length of the randomized string
    
    Returns:
        A random string
    """
    rand_str = ""
    possible_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"

    for _ in range(length):
        rand_str += possible_chars[random.randint(0, len(possible_chars) - 1)]
    
    return rand_str

#  }}} generate_random_string # 

#  token_expired {{{ # 

def token_expired(token_obtained_at, valid_for):
    """Returns True if token expired, False if otherwise

    Args:
        token_obtained_at: datetime object representing the date and time when the token was obtained
        valid_for: the time duration for which the token is valid, in seconds
    """
    time_elapsed = (datetime.today() - token_obtained_at).total_seconds()
    return time_elapsed >= valid_for

#  }}} token_expired # 

#  index {{{ # 

# Create your views here.
def index(request):
    return render(request, 'spotifyvis/index.html')

#  }}}  index # 

#  login {{{ # 

def login(request):

    # use a randomly generated state string to prevent cross-site request forgery attacks
    state_str = generate_random_string(16)
    request.session['state_string'] = state_str 

    payload = {
        'client_id': os.environ['SPOTIFY_CLIENT_ID'],
        'response_type': 'code',
        'redirect_uri': 'http://localhost:8000/callback',
        'state': state_str,
        'scope': 'user-library-read',
        'show_dialog': False
    }

    params = urllib.parse.urlencode(payload) # turn the payload dict into a query string
    authorize_url = "https://accounts.spotify.com/authorize/?{}".format(params)
    return redirect(authorize_url)

#  }}} login # 

#  callback {{{ # 

def callback(request):
    # Attempt to retrieve the authorization code from the query string
    try:
        code = request.GET['code']
    except KeyError:
        return HttpResponseBadRequest("<h1>Problem with login</h1>")

    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'http://localhost:8000/callback',
        'client_id': os.environ['SPOTIFY_CLIENT_ID'],
        'client_secret': os.environ['SPOTIFY_CLIENT_SECRET'],
    }

    response = requests.post('https://accounts.spotify.com/api/token', data = payload).json()
    # despite its name, datetime.today() returns a datetime object, not a date object
    # use datetime.strptime() to get a datetime object from a string
    request.session['token_obtained_at'] = datetime.strftime(datetime.today(), TIME_FORMAT) 
    request.session['access_token'] = response['access_token']
    request.session['refresh_token'] = response['refresh_token']
    request.session['valid_for'] = response['expires_in']
    #  print(response)

    return redirect('user_data')

#  }}} callback # 

#  user_data {{{ # 

def user_data(request):
    token_obtained_at = datetime.strptime(request.session['token_obtained_at'], TIME_FORMAT)
    valid_for = int(request.session['valid_for'])

    if token_expired(token_obtained_at, valid_for):
        req_body = {
            'grant_type': 'refresh_token',
            'refresh_token': request.session['refresh_token'],
            'client_id': os.environ['SPOTIFY_CLIENT_ID'],
            'client_secret': os.environ['SPOTIFY_CLIENT_SECRET']
        }
        
        refresh_token_response = requests.post('https://accounts.spotify.com/api/token', data = req_body).json()
        request.session['access_token'] = refresh_token_response['access_token']
        request.session['valid_for'] = refresh_token_response['expires_in']

    auth_token_str = "Bearer " + request.session['access_token']
    headers = {
        'Authorization': auth_token_str
    }

    user_data_response = requests.get('https://api.spotify.com/v1/me', headers = headers).json()
    context = {
        'user_name': user_data_response['display_name'],
        'id': user_data_response['id'],
    }

    tracks_to_query = 50
    parse_library(headers, tracks_to_query)
    return render(request, 'spotifyvis/user_data.html', context)

#  }}} user_data  # 

#  parse_library {{{ # 

def parse_library(headers, tracks):
    """Scans user's library for certain number of tracks to update library_stats with.

    :headers: For API call.
    :tracks: Number of tracks to get from user's library.
    :returns: None

    """
    #  TODO: implement importing entire library with 0 as tracks param
    # number of tracks to get with each call
    limit = 50
    # keeps track of point to get songs from
    offset = 0
    payload = {'limit': str(limit)}
    for i in range(0, tracks, limit):
        payload['offset'] = str(offset)
        saved_tracks_response = requests.get('https://api.spotify.com/v1/me/tracks', headers=headers, params=payload).json()
        for track_dict in saved_tracks_response['items']:
            get_track_info(track_dict['track'])
            #  get_genre(headers, track_dict['track']['album']['id'])
            for artist_dict in track_dict['track']['artists']:
                increase_artist_count(headers, artist_dict['name'], artist_dict['id'])
        # calculates num_songs with offset + songs retrieved
        library_stats['num_songs'] = offset + len(saved_tracks_response['items'])
        offset += limit

    pprint.pprint(library_stats)

#  }}} parse_library # 

#  increase_nested_key {{{ # 

def increase_nested_key(top_key, nested_key):
    """Increases count for the value of library_stats[top_key][nested_key]. Checks if nested_key exists already and takes
    appropriate action.

    :top_key: First key of library_stats.
    :nested_key: Key in top_key's dict for which we want to increase value of.
    :returns: None

    """
    if nested_key not in library_stats[top_key]:
        library_stats[top_key][nested_key] = 1
    else:
        library_stats[top_key][nested_key] += 1

#  }}} increase_nested_key # 

#  increase_artist_count {{{ # 

def increase_artist_count(headers, artist_name, artist_id):
    """Increases count for artist and genre in library_stats. Also looks up genre of artist if new key.

    :headers: For making the API call.
    :artist_name: Artist to increase count for.
    :artist_id: The Spotify ID for the artist.
    :returns: None

    """
    if artist_name not in library_stats['artists']:
        library_stats['artists'][artist_name] = {}
        library_stats['artists'][artist_name]['count'] = 1
        # set genres for artist
        artist_response = requests.get('https://api.spotify.com/v1/artists/' + artist_id, headers=headers).json()
        library_stats['artists'][artist_name]['genres'] = artist_response['genres']
    else:
        library_stats['artists'][artist_name]['count'] += 1

    # update genre counts
    for genre in library_stats['artists'][artist_name]['genres']:
        increase_nested_key('genres', genre)

#  }}} increase_artist_count # 

#  get_track_info {{{ # 

def get_track_info(track_dict):
    """Get all the info from the track_dict directly returned by the API call in parse_library.

    :track_dict: Dict returned from the API call containing the track info.
    :returns: None

    """
    #  popularity
    library_stats['popularity'].append(track_dict['popularity'])

    # year
    year_released = track_dict['album']['release_date'].split('-')[0]
    increase_nested_key('year_released', year_released)
    
    # artist
    #  artist_names = [artist['name'] for artist in track_dict['artists']]
    #  for artist_name in artist_names:
        #  increase_nested_key('artists', artist_name)

    # runtime
    library_stats['total_runtime'] += float(track_dict['duration_ms']) / 60

#  }}} get_track_info # 

#  get_genre {{{ # 

# Deprecated. Will remove in next commit. I queried 300 albums and none of them had genres. 
# The organization app gets the genre from the artist, and I've implemented other functions
# to do the same.
def get_genre(headers, album_id):
    """Updates library_stats with this track's genre.

    :headers: For making the API call.
    :album_id: The Spotify ID for the album.
    :returns: None

    """
    album_response = requests.get('https://api.spotify.com/v1/albums/' + album_id, headers=headers).json()
    pprint.pprint(album_response['genres'])
    for genre in album_response['genres']:
        #  print(genre)
        increase_nested_key('genres', genre);

#  }}} get_genre # 

#  def calculate_genres_from_artists(headers):
    #  """Tallies up genre counts based on artists in library_stats.

    #  :headers: For making the API call.
    #  :returns: None

    #  """
    #  album_response = requests.get('https://api.spotify.com/v1/albums/' + album_id, headers=headers).json()
