import string
import random
import requests

from .models import User

def get_user_context(user_obj):
    """Get context for rendering with User's ID and secret.

    :user_obj: User object to make context for.
    :returns: context to pass back to HTML file.

    """
    return { 'user_id': user_obj.id, 'user_secret': user_obj.secret, }

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

#  create_user {{{ # 


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

#  }}} create_user # 

def get_scan_context(request):
    """Get context for rendering scan page.

    :request: 
    :returns: Context with upload form and user info.

    """
    context = { 'user_id': request.session['user_id'], 
            'user_secret': request.session['user_secret'], }
    # set hidden user field to current user
    context['form'] = HistoryUploadForm(initial=
            { 'user': User.objects.get(id=request.session['user_id']) }) 
    return context
