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
from django.http import HttpResponseBadRequest
from .models import *

#  }}} imports # 

TIME_FORMAT = '%Y-%m-%d-%H-%M-%S'
TRACKS_TO_QUERY = 200

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

#  index {{{ # 

# Create your views here.
def index(request):
    return render(request, 'login/index.html')

#  }}}  index # 

#  spotify_login {{{ # 

def spotify_login(request):
    """ Step 1 in authorization flow: Have your application request
    authorization; the user logs in and authorizes access.
    """
    # use a randomly generated state string to prevent cross-site request forgery attacks
    state_str = generate_random_string(16)
    request.session['state_string'] = state_str 

    payload = {
        'client_id': os.environ['SPOTIFY_CLIENT_ID'],
        'response_type': 'code',
        'redirect_uri': 'http://localhost:8000/login/callback',
        'state': state_str,
        'scope': 'user-library-read',
        'show_dialog': False
    }

    params = urllib.parse.urlencode(payload) # turn the payload dict into a query string
    authorize_url = "https://accounts.spotify.com/authorize/?{}".format(params)
    return redirect(authorize_url)

#  }}} spotify_login # 

def callback(request):
    """ Step 2 in authorization flow: Have your application request refresh and
    access tokens; Spotify returns access and refresh tokens. 
    """
    # Attempt to retrieve the authorization code from the query string
    try:
        code = request.GET['code']
    except KeyError:
        return HttpResponseBadRequest("<h1>Problem with login</h1>")

    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'http://localhost:8000/login/callback',
        'client_id': os.environ['SPOTIFY_CLIENT_ID'],
        'client_secret': os.environ['SPOTIFY_CLIENT_SECRET'],
    }

    token_response = requests.post('https://accounts.spotify.com/api/token', data=payload).json()
    user_obj = create_user(token_response['refresh_token'],
            token_response['access_token'],
            token_response['expires_in']) 

    context = { 
            'user_id': user_obj.id, 
            'user_secret': user_obj.secret, 
            }
    return render(request, 'login/scan.html', context)
    #  return redirect('user/' + user_obj.secret)


def create_user(refresh_token, access_token, access_expires_in):
    """Create a User object based on information returned from Step 2 (callback
    function) of auth flow.

    :refresh_token: Used to renew access tokens.
    :access_token: Used in Spotify API calls.
    :access_expires_in: How long the access token last in seconds.

    :returns: The newly created User object.

    """
    profile_response = requests.get('https://api.spotify.com/v1/me',
            headers={'Authorization': "Bearer " + access_token}).json()
    user_id = profile_response['id']

    try:
        user_obj = User.objects.get(id=user_id)
    except User.DoesNotExist:
        # Python docs recommends 32 bytes of randomness against brute
        # force attacks
        user_obj = User.objects.create(
                id=user_id,
                secret=secrets.token_urlsafe(32),
                refresh_token=refresh_token,
                access_token=access_token,
                access_expires_in=access_expires_in,
                )

    return user_obj

#  admin_graphs {{{ # 

def admin_graphs(request):
    """TODO
    """
    user_id = "polarbier"
    #  user_id = "chrisshyi13"
    user_obj = User.objects.get(user_id=user_id)
    context = {
        'user_id': user_id,
        'user_secret': user_obj.user_secret,
    }
    update_track_genres(user_obj)
    return render(request, 'login/logged_in.html', context)

#  }}} admin_graphs  # 
