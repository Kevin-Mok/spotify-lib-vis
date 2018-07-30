from django.test import TestCase
from api.models import Track, Genre, Artist
from login.models import User
from api import utils
import math
import pprint

class GenreDataTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
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

        pop_genre = Genre.objects.create(name='pop', num_songs=3)
        pop_artist1 = Artist.objects.create(id='art4', name="Taylor Swift")
        pop_artist2 = Artist.objects.create(id='art5', name="Justin Bieber")
        pop_artist3 = Artist.objects.create(id='art6', name="Rihanna")

        pop_track_1 = Track.objects.create(id='track4', year=2013,
                                       popularity=5, runtime=20,
                                       name='poptrack1',
                                       genre=pop_genre)
        pop_track_1.users.add(test_user)
        pop_track_1.artists.add(pop_artist1)
        pop_track_1.artists.add(pop_artist2)

        pop_track_2 = Track.objects.create(id='track5', year=2013,
                                           popularity=5, runtime=20,
                                           name='poptrack2',
                                           genre=pop_genre)
        pop_track_2.users.add(test_user)
        pop_track_2.artists.add(pop_artist3)
        pop_track_2.artists.add(pop_artist2)
        pop_track_2.artists.add(pop_artist1)

        pop_track_3 = Track.objects.create(id='track6', year=2013,
                                           popularity=5, runtime=20,
                                           name='poptrack3',
                                           genre=pop_genre)
        pop_track_3.users.add(test_user)
        pop_track_3.artists.add(pop_artist3)
        pop_track_3.artists.add(pop_artist2)
        pop_track_3.artists.add(pop_artist1)


    def test_get_artist_counts_two_genres(self):
        test_user = User.objects.get(id='chrisshi')
        artist_counts = utils.get_artists_in_genre(test_user, 'classical')
        # pprint.pprint(artist_counts)
        self.assertTrue(math.isclose(artist_counts['Beethoven'], 1.3, rel_tol=0.05))
        self.assertTrue(math.isclose(artist_counts['Mozart'], 0.85, rel_tol=0.05))
        self.assertTrue(math.isclose(artist_counts['Chopin'], 0.85, rel_tol=0.05))
        self.assertTrue(math.isclose(sum(artist_counts.values()), 3, rel_tol=0.01))
        # test the pop genre
        artist_counts = utils.get_artists_in_genre(test_user, 'pop')
        self.assertTrue(math.isclose(artist_counts['Taylor Swift'], 1.125, rel_tol=0.05))
        self.assertTrue(math.isclose(artist_counts['Justin Bieber'], 1.125, rel_tol=0.05))
        self.assertTrue(math.isclose(artist_counts['Rihanna'], 0.75, rel_tol=0.05))
        self.assertTrue(math.isclose(sum(artist_counts.values()), 3, rel_tol=0.01))