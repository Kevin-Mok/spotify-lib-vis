from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest
import math
import random
import requests
import os
import urllib
import datetime

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


def token_expired(token_obtained_at, valid_for):
    """Returns True if token expired, False if otherwise

    Args:
        token_obtained_at: datetime object representing the date and time when the token was obtained
        valid_for: the time duration for which the token is valid, in seconds
    """
    time_elapsed = (datetime.datetime.today() - token_obtained_at).seconds
    return time_elapsed >= valid_for


# Create your views here.
def index(request):
    return render(request, 'spotifyvis/index.html')


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
    request.session['token_obtained_at'] = str(datetime.datetime.today()) 
    request.session['access_token'] = response['access_token']
    request.session['refresh_token'] = response['refresh_token']
    request.session['valid_for'] = response['expires_in']
    print(response)

    auth_token_str = "Bearer " + response['access_token']
    headers = {
        'Authorization': auth_token_str
    }

    user_data_response = requests.get('https://api.spotify.com/v1/me', headers = headers).json()
    context = {
        'user_name': user_data_response['display_name'],
        'id': user_data_response['id'],
    }
    return render(request, 'spotifyvis/user_data.html', context)