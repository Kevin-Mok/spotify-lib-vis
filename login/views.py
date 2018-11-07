#  imports {{{ # 

import math
import os
import urllib
import secrets
import pprint
from datetime import datetime

from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest
from .models import *
from .utils import *

#  }}} imports # 

TIME_FORMAT = '%Y-%m-%d-%H-%M-%S'
TRACKS_TO_QUERY = 200
AUTH_SCOPE = ['user-library-read', 'user-read-recently-played',]

#  index {{{ # 

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
        'scope': " ".join(AUTH_SCOPE),
        'show_dialog': False
    }

    params = urllib.parse.urlencode(payload) # turn the payload dict into a query string
    authorize_url = "https://accounts.spotify.com/authorize/?{}".format(params)
    return redirect(authorize_url)

#  }}} spotify_login # 

#  callback {{{ # 

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
    
    request.session['user_id'] = user_obj.id
    request.session['user_secret'] = user_obj.secret

    return render(request, 'login/scan.html', get_user_context(user_obj))

#  }}} callback # 

#  admin_graphs {{{ # 

def admin_graphs(request):
    """TODO
    """
    user_id = "polarbier"
    #  user_id = "chrisshyi13"

    request.session['user_id'] = user_id
    #  request.session['user_secret'] = user_obj.secret
    request.session['user_secret'] = User.objects.get(id=user_id).secret
    user_obj = User.objects.get(id=user_id)
    return render(request, 'graphs/logged_in.html', get_user_context(user_obj))

#  }}} admin_graphs  # 
