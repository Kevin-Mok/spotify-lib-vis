#  imports {{{ # 
import requests
import math
import pprint

from .models import Artist, User, Track, AudioFeatures
from django.db.models import Count, Q
from django.http import JsonResponse
from django.core import serializers
import json

#  }}} imports # 

#  parse_library {{{ # 


def parse_library(headers, tracks, user):
    """Scans user's library for certain number of tracks and store the information in a database

    :headers: For API call.
    :tracks: Number of tracks to get from user's library.
    :user: a User object representing the user whose library we are parsing

    :returns: None

    """
    #  TODO: implement importing entire library with 0 as tracks param
    # number of tracks to get with each call
    limit = 5
    # keeps track of point to get songs from
    offset = 0
    payload = {'limit': str(limit)}

    # iterate until hit requested num of tracks
    for _ in range(0, tracks, limit):
        payload['offset'] = str(offset)
        # get current set of tracks
        saved_tracks_response = requests.get('https://api.spotify.com/v1/me/tracks', headers=headers, params=payload).json()

        # TODO: refactor the for loop body into helper function
        # iterate through each track
        for track_dict in saved_tracks_response['items']:
            # update artist info before track so that Track object can reference
            # Artist object
            track_artists = []
            for artist_dict in track_dict['track']['artists']:
                artist_obj, artist_created = Artist.objects.get_or_create(
                    artist_id=artist_dict['id'],
                    name=artist_dict['name'],
                    )

                #  update_artist_genre(headers, artist_obj)
                # get_or_create() returns a tuple (obj, created)
                track_artists.append(artist_obj)
            
            top_genre = get_top_genre(headers,
                    track_dict['track']['artists'][0]['id'])
            track_obj, track_created = save_track_obj(track_dict['track'], 
                    track_artists, top_genre, user)

            # if a new track is not created, the associated audio feature does not need to be created again
            if track_created:
                save_audio_features(headers, track_dict['track']['id'], track_obj)
            """
            TODO: Put this logic in another function
            # Audio analysis could be empty if not present in Spotify database
            if len(audio_features_dict) != 0:
                # Track the number of audio analyses for calculating
                # audio feature averages and standard deviations on the fly
                feature_data_points += 1
                for feature, feature_data in audio_features_dict.items():
                    update_audio_feature_stats(feature, feature_data, 
                            feature_data_points, library_stats)
            """
        # calculates num_songs with offset + songs retrieved
        offset += limit
    #  pprint.pprint(library_stats)

#  }}} parse_library # 

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
            genre=top_genre,
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

def save_audio_features(headers, track_id, track):
    """Creates and saves a new AudioFeatures object

    Args:
        headers: headers containing the API token
        track_id: the id of the soundtrack, needed to query the Spotify API
        track: Track object to associate with the new AudioFeatures object
        
    """
    
    response = requests.get("https://api.spotify.com/v1/audio-features/{}".format(track_id), headers = headers).json()
    if 'error' in response:
        return

    # Data that we don't need
    useless_keys = [ 
        "key", "mode", "type", "liveness", "id", "uri", "track_href", "analysis_url", "time_signature",
    ]
    audio_features_entry = AudioFeatures()
    audio_features_entry.track = track
    for key, val in response.items():
        if key not in useless_keys:
            setattr(audio_features_entry, key, val)
    audio_features_entry.save()


#  }}} get_audio_features # 

#  update_std_dev {{{ # 

def update_std_dev(cur_mean, cur_std_dev, new_data_point, sample_size):
    """Calculates the standard deviation for a sample without storing all data points

    Args:
        cur_mean: the current mean for N = (sample_size - 1)
        cur_std_dev: the current standard deviation for N = (sample_size - 1)
        new_data_point: a new data point
        sample_size: sample size including the new data point
    
    Returns:
        (new_mean, new_std_dev)
    """
    # This is an implementation of Welford's method
    # http://jonisalonen.com/2013/deriving-welfords-method-for-computing-variance/
    new_mean = ((sample_size - 1) * cur_mean + new_data_point) / sample_size
    delta_variance = (new_data_point - new_mean) * (new_data_point - cur_mean)
    new_std_dev = math.sqrt(
        (math.pow(cur_std_dev, 2) * (sample_size - 2) + delta_variance) / (
        sample_size - 1
    ))
    return new_mean, new_std_dev

#  }}} update_std_dev # 

#  update_audio_feature_stats {{{ # 

def update_audio_feature_stats(feature, new_data_point, sample_size, library_stats):
    """Updates the audio feature statistics in library_stats

    Args:
        feature: the audio feature to be updated (string)
        new_data_point: new data to update the stats with
        sample_size: sample size including the new data point
        library_stats Dictionary containing the data mined from user's Spotify library

    
    Returns:
        None
    """
    # first time the feature is considered
    if sample_size < 2:
        library_stats['audio_features'][feature] = {
            "average": new_data_point,
            "std_dev": 0,
        }
    else:
        cur_mean = library_stats['audio_features'][feature]['average']
        cur_std_dev = library_stats['audio_features'][feature]['std_dev']
        new_mean, new_std_dev = update_std_dev(cur_mean, cur_std_dev, new_data_point, sample_size)

        library_stats['audio_features'][feature] = {
            "average": new_mean,
            "std_dev": new_std_dev
        }

#  }}} update_audio_feature_stats # 

#  increase_nested_key {{{ # 

def increase_nested_key(top_key, nested_key, library_stats, amount=1):
    """Increases count for the value of library_stats[top_key][nested_key]. Checks if nested_key exists already and takes
    appropriate action.

    :top_key: First key of library_stats.
    :nested_key: Key in top_key's dict for which we want to increase value of.
    :library_stats: Dictionary containing the data mined from user's Spotify library

    :returns: None

    """
    if nested_key not in library_stats[top_key]:
        library_stats[top_key][nested_key] = amount
    else:
        library_stats[top_key][nested_key] += amount

#  }}} increase_nested_key # 

#  increase_artist_count {{{ # 

def increase_artist_count(headers, artist_name, artist_id, library_stats):
    """Increases count for artist in library_stats and stores the artist_id. 

    :headers: For making the API call.
    :artist_name: Artist to increase count for.
    :artist_id: The Spotify ID for the artist.
    :library_stats: Dictionary containing the data mined from user's Spotify library

    :returns: None

    """
    if artist_name not in library_stats['artists']:
        library_stats['artists'][artist_name] = {}
        library_stats['artists'][artist_name]['count'] = 1
        library_stats['artists'][artist_name]['id'] = artist_id
    else:
        library_stats['artists'][artist_name]['count'] += 1

#  }}} increase_artist_count # 

#  update_popularity_stats {{{ # 

def update_popularity_stats(new_data_point, library_stats, sample_size):
    """Updates the popularity statistics in library_stats

    Args:
        new_data_point: new data to update the popularity stats with
        library_stats: Dictionary containing data mined from user's Spotify library
        sample_size: The sample size including the new data
    
    Returns:
        None
    """
    if sample_size < 2:
        library_stats['popularity'] = {
            "average": new_data_point,
            "std_dev": 0,
        }
    else :
        cur_mean_popularity = library_stats['popularity']['average']
        cur_popularity_stdev = library_stats['popularity']['std_dev']
        new_mean, new_std_dev = update_std_dev(
            cur_mean_popularity, cur_popularity_stdev, new_data_point, sample_size)
        library_stats['popularity'] = {
            "average": new_mean,
            "std_dev": new_std_dev,
        }

#  }}}  update_popularity_stats # 

#  get_track_info {{{ # 

def get_track_info(track_dict, library_stats, sample_size):
    """Get all the info from the track_dict directly returned by the API call in parse_library.

    :track_dict: Dict returned from the API call containing the track info.
    :library_stats: Dictionary containing the data mined from user's Spotify library
    :sample_size: The sample size so far including this track

    :returns: None

    """
    # popularity
    update_popularity_stats(track_dict['popularity'], library_stats, sample_size)
        
    # year
    year_released = track_dict['album']['release_date'].split('-')[0]
    increase_nested_key('year_released', year_released, library_stats)
    
    # runtime
    library_stats['total_runtime'] += float(track_dict['duration_ms']) / (1000 * 60)

#  }}} get_track_info # 

#  update_artist_genre {{{ # 

def update_artist_genre(headers, artist_obj):
    """Updates the top genre for an artist by querying the Spotify API

    :headers: For making the API call.
    :artist_obj: the Artist object whose genre field will be updated 

    :returns: None

    """
    artist_response = requests.get('https://api.spotify.com/v1/artists/' + artist_obj.artist_id, headers=headers).json()
    # update genre for artist in database with top genre
    if len(artist_response['genres']) > 0:
        artist_obj.genre = artist_response['genres'][0]
        artist_obj.save()

#  }}} # 

#  get_top_genre {{{ # 

def get_top_genre(headers, top_artist_id):
    """Updates the top genre for a track by querying the Spotify API

    :headers: For making the API call.
    :top_artist: The first artist's (listed in the track) Spotify ID.

    :returns: The first genre listed for the top_artist.

    """
    artist_response = requests.get('https://api.spotify.com/v1/artists/' +
            top_artist_id, headers=headers).json()
    if len(artist_response['genres']) > 0:
        return artist_response['genres'][0]
    else:
        return "undefined"

#  }}} # 

#  process_library_stats {{{ # 


def process_library_stats(library_stats):
    """Processes library_stats into format more suitable for D3 consumption

    Args:
        library_stats: Dictionary containing the data mined from user's Spotify library
    
    Returns:
        A new dictionary that contains the data in library_stats, in a format more suitable for D3 consumption
    """
    processed_library_stats = {}
    for key in library_stats:
        if key == 'artists' or key == 'genres' or key == 'year_released':
            for inner_key in library_stats[key]:
                if key not in processed_library_stats:
                    processed_library_stats[key] = []
                processed_item_key = '' # identifier key for each dict in the list
                count = 0
                if 'artist' in key:
                    processed_item_key = 'name'
                    count = library_stats[key][inner_key]['count']
                elif 'genre' in key:
                    processed_item_key = 'genre'
                    count = library_stats[key][inner_key]
                else:
                    processed_item_key = 'year'
                    count = library_stats[key][inner_key]

                processed_library_stats[key].append({
                    processed_item_key: inner_key,
                    "count": count
                })
        elif key == 'audio_features':
            for audio_feature in library_stats[key]:
                if 'audio_features' not in processed_library_stats:
                    processed_library_stats['audio_features'] = []
                processed_library_stats['audio_features'].append({
                    'feature': audio_feature,
                    'average': library_stats[key][audio_feature]['average'],
                    'std_dev': library_stats[key][audio_feature]['std_dev']
                })
        # TODO: Not sure about final form for 'popularity'
        # elif key == 'popularity':
        #     processed_library_stats[key] = []
        #     processed_library_stats[key].append({

        #     })
        elif key == 'num_songs' or key == 'total_runtime' or key == 'popularity':
            processed_library_stats[key] = library_stats[key]
    
    return processed_library_stats

#  }}} process_library_stats # 

def get_artists_in_genre(user, genre):
    """Return count of artists in genre.

    :genre: genre to count artists for.

    :returns: dict of artists in the genre along with the number of songs they
    have. 
    """
    artist_counts = (Artist.objects.filter(track__users=user).distinct()
                     .filter(track__genre=genre).distinct()
                     .annotate(num_songs=Count('track'))
                     )
    processed_artist_counts = [{'name': artist.name, 'num_songs': artist.num_songs} for artist in artist_counts]
    #  pprint.pprint(processed_artist_counts)
    return processed_artist_counts
