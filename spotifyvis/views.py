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
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.db.models import Count, Q
from .utils import parse_library, process_library_stats, get_artists_in_genre
from .models import User, Track, AudioFeatures, Artist 

#  }}} imports # 

TIME_FORMAT = '%Y-%m-%d-%H-%M-%S'
TRACKS_TO_QUERY = 15

#  generate_random_string {{{ # 


def generate_random_string(length):
    """Generates a random string of a certain length

    Args:
        length: the desired length of the randomized string
    
    Returns:
        A random string
    """
    all_chars = string.ascii_letters + string.digits
    rand_str = "".join(random.choice(all_chars) for _ in range(length)) 
    
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

    response = requests.post('https://accounts.spotify.com/api/token', data=payload).json()
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
    request.session['user_id'] = user_data_response['id']  # store the user_id so it may be used to create model
    #  request.session['user_name'] = user_data_response['display_name']

    try:
        user = User.objects.get(user_id=user_data_response['id'])
    except User.DoesNotExist:
        # Python docs recommends 32 bytes of randomness against brute force attacks
        user = User(user_id=user_data_response['id'], user_secret=secrets.token_urlsafe(32))
        user.save()

    context = {
        'id': user_data_response['id'],
        'user_secret': user.user_secret,
    }

    parse_library(headers, TRACKS_TO_QUERY, user)
    return render(request, 'spotifyvis/user_data.html', context)

#  }}} user_data  # 

#  test_db {{{ # 

def test_db(request):
    """TODO
    """
    #  user_id = "polarbier"
    user_id = "chrisshyi13"
    context = {
        'user_secret': User.objects.get(user_id=user_id).user_secret,
    }
    return render(request, 'spotifyvis/test_db.html', context)

#  }}} test_db # 

#  get_artist_data {{{ # 

def get_artist_data(request, user_secret):
    """TODO
    """
    user = User.objects.get(user_id=user_secret)
    artist_counts = Artist.objects.annotate(num_songs=Count('track',
        filter=Q(track__users=user)))
    processed_artist_counts = [{'name': artist.name,
        'num_songs': artist.num_songs} for artist in artist_counts]
    return JsonResponse(data=processed_artist_counts, safe=False) 

#  }}} get_artist_data # 

#  get_audio_feature_data {{{ # 

def get_audio_feature_data(request, audio_feature, client_secret):
    """Returns all data points for a given audio feature

    Args:
        request: the HTTP request
        audio_feature: The audio feature to be queried
        client_secret: client secret, used to identify the user
    """
    user = User.objects.get(user_secret=client_secret)
    user_tracks = Track.objects.filter(users=user)
    response_payload = {
        'data_points': [],
    }
    for track in user_tracks:
        audio_feature_obj = AudioFeatures.objects.get(track=track)
        response_payload['data_points'].append(getattr(audio_feature_obj, audio_feature))
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
        genre_dict['artists'] = get_artists_in_genre(user, genre_dict['genre'])
    pprint.pprint(list(genre_counts))
    return JsonResponse(data=list(genre_counts), safe=False) 

#  }}} get_genre_data  # 
