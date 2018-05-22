import requests
import math
import pprint

#  parse_library {{{ # 

def parse_library(headers, tracks, library_stats):
    """Scans user's library for certain number of tracks to update library_stats with.

    :headers: For API call.
    :tracks: Number of tracks to get from user's library.
    :library_stats: Dictionary containing the data mined from user's library 

    :returns: None

    """
    #  TODO: implement importing entire library with 0 as tracks param
    # number of tracks to get with each call
    limit = 5
    # keeps track of point to get songs from
    offset = 0
    payload = {'limit': str(limit)}
    for _ in range(0, tracks, limit):
        payload['offset'] = str(offset)
        saved_tracks_response = requests.get('https://api.spotify.com/v1/me/tracks', headers=headers, params=payload).json()
        num_samples = offset
        for track_dict in saved_tracks_response['items']:
            # Track the number of samples for calculating
            # audio feature averages and standard deviations on the fly
            num_samples += 1 
            get_track_info(track_dict['track'], library_stats)
            #  get_genre(headers, track_dict['track']['album']['id'])
            audio_features_dict = get_audio_features(headers, track_dict['track']['id'])
            for feature, feature_data in audio_features_dict.items():
                update_audio_feature_stats(feature, feature_data, num_samples, library_stats)
            for artist_dict in track_dict['track']['artists']:
                increase_artist_count(headers, artist_dict['name'], artist_dict['id'], library_stats)
        # calculates num_songs with offset + songs retrieved
        library_stats['num_songs'] = offset + len(saved_tracks_response['items'])
        offset += limit
    calculate_genres_from_artists(headers, library_stats)
    pprint.pprint(library_stats)

#  }}} parse_library # 

def get_audio_features(headers, track_id):
    """Returns the audio features of a soundtrack

    Args:
        headers: headers containing the API token
        track_id: the id of the soundtrack, needed to query the Spotify API
        
    Returns:
        A dictionary with the features as its keys
    """
    
    response = requests.get("https://api.spotify.com/v1/audio-features/{}".format(track_id), headers = headers).json()
    features_dict = {}

    # Data that we don't need
    useless_keys = [ 
        "key", "mode", "type", "liveness", "id", "uri", "track_href", "analysis_url", "time_signature",
    ]
    for key, val in response.items():
        if key not in useless_keys:
            features_dict[key] = val

    return features_dict


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

        library_stats['audio_features'][feature]['average'] = new_mean
        library_stats['audio_features'][feature]['std_dev'] = new_std_dev


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

#  get_track_info {{{ # 

def get_track_info(track_dict, library_stats):
    """Get all the info from the track_dict directly returned by the API call in parse_library.

    :track_dict: Dict returned from the API call containing the track info.
    :library_stats: Dictionary containing the data mined from user's Spotify library

    :returns: None

    """
    #  popularity
    library_stats['popularity'].append(track_dict['popularity'])

    # year
    year_released = track_dict['album']['release_date'].split('-')[0]
    increase_nested_key('year_released', year_released, library_stats)
    
    # artist
    #  artist_names = [artist['name'] for artist in track_dict['artists']]
    #  for artist_name in artist_names:
        #  increase_nested_key('artists', artist_name)

    # runtime
    library_stats['total_runtime'] += float(track_dict['duration_ms']) / 60

#  }}} get_track_info # 

#  calculate_genres_from_artists {{{ # 

def calculate_genres_from_artists(headers, library_stats):
    """Tallies up genre counts based on artists in library_stats.

    :headers: For making the API call.
    :library_stats: Dictionary containing the data mined from user's Spotify library

    :returns: None

    """
    for artist_entry in library_stats['artists'].values():
        artist_response = requests.get('https://api.spotify.com/v1/artists/' + artist_entry['id'], headers=headers).json()
        # increase each genre count by artist count
        for genre in artist_response['genres']:
            increase_nested_key('genres', genre, library_stats, artist_entry['count'])

#  }}} calculate_genres_from_artists # 