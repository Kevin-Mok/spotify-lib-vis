from django.shortcuts import render, redirect
from django.http import HttpResponse
import math
import random
import requests
import os
import urllib

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


# Create your views here.
def index(request):
    return render(request, 'spotifyvis/index.html')


def login(request):

    state_str = generate_random_string(16)
    # use a randomly generated state string to prevent cross-site request forgery attacks
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
    return HttpResponse("At callback")