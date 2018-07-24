from django.test import TestCase
from api.models import Track, Genre, Artist
from login.models import User
from api import utils
import math
import pprint

class GenreDataTestCase(TestCase):

    def setUp(self):
        test_user = User.objects.create(id="chrisshi", refresh_token="blah", access_token="blah",
                         access_expires_in=10)
        genre = Genre.objects.create(name="classical", num_songs=3)
        artist_1 = Artist.objects.create(id='art1', name="Beethoven")
        artist_2 = Artist.objects.create(id='art2', name="Mozart")
        artist_3 = Artist.objects.create(id='art3', name='Chopin')

        track_1 = Track.objects.create(id='track1', year=2013,
                                       popularity=5, runtime=20,
                                       name='concerto1',
                                       genre=genre)
        track_1.users.add(test_user)
        track_1.artists.add(artist_1)
        track_1.artists.add(artist_2)

        track_2 = Track.objects.create(id='track2', year=2013,
                                       popularity=5, runtime=20,
                                       name='concerto2',
                                       genre=genre)
        track_2.users.add(test_user)
        track_2.artists.add(artist_2)
        track_2.artists.add(artist_3)
        track_2.artists.add(artist_1)

        track_3 = Track.objects.create(id='track3', year=2013,
                                       popularity=5, runtime=20,
                                       name='concerto3',
                                       genre=genre)
        track_3.users.add(test_user)
        track_3.artists.add(artist_1)
        track_3.artists.add(artist_3)

    def test_get_artist_counts_in_genre(self):
        test_user = User.objects.get(id='chrisshi')
        artist_counts = utils.get_artists_in_genre(test_user, 'classical', 10)
        # pprint.pprint(artist_counts)
        self.assertTrue(math.isclose(artist_counts['Beethoven'], 1.3, rel_tol=0.05))
        self.assertTrue(math.isclose(artist_counts['Mozart'], 0.85, rel_tol=0.05))
        self.assertTrue(math.isclose(artist_counts['Chopin'], 0.85, rel_tol=0.05))
        self.assertTrue(math.isclose(sum(artist_counts.values()), 3, rel_tol=0.01))