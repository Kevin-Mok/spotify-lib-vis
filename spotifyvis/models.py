from django.db import models

# id's are 22 in length in examples but set to 30 for buffer
MAX_ID = 30

#  Artist {{{ # 


class Artist(models.Model):
    class Meta:
        verbose_name = "Artist"
        verbose_name_plural = "Artists"

    artist_id = models.CharField(primary_key=True, max_length=MAX_ID)
    # unique since only storing one genre per artist right now
    name = models.CharField(unique=True, max_length=50)

    def __str__(self):
        return self.name

#  }}} Artist # 

#  User {{{ # 

class User(models.Model):
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    user_id = models.CharField(primary_key=True, max_length=MAX_ID) # the user's Spotify ID
    user_secret = models.CharField(max_length=30, default='')

    def __str__(self):
        return self.user_id

#  }}} User # 

class Genre(models.Model):
            
    class Meta:
        verbose_name = "Genre"
        verbose_name_plural = "Genres"

    name = models.CharField(primary_key=True, max_length=50)
    num_songs = models.PositiveIntegerField()

    def __str__(self):
        return self.name

#  Track {{{ # 

class Track(models.Model):
    
    class Meta:
        verbose_name = "Track"
        verbose_name_plural = "Tracks"

    track_id = models.CharField(primary_key=True, max_length=MAX_ID)
    #  artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    artists = models.ManyToManyField(Artist, blank=True)
    year = models.PositiveSmallIntegerField()
    popularity = models.PositiveSmallIntegerField()
    runtime = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=200)
    users = models.ManyToManyField(User, blank=True)
    #  genre = models.CharField(max_length=30)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, blank=True,
            null=True)

    def __str__(self):
        return self.name 

#  }}} Track # 

#  AudioFeatures {{{ # 

class AudioFeatures(models.Model):
        
    class Meta:
        verbose_name = "AudioFeatures"
        verbose_name_plural = "AudioFeatures"

    track = models.OneToOneField(Track, on_delete=models.CASCADE, primary_key=True,)
    acousticness = models.DecimalField(decimal_places=3, max_digits=3)
    danceability = models.DecimalField(decimal_places=3, max_digits=3)
    energy = models.DecimalField(decimal_places=3, max_digits=3)
    instrumentalness = models.DecimalField(decimal_places=3, max_digits=3)
    loudness = models.DecimalField(decimal_places=3, max_digits=6)
    speechiness = models.DecimalField(decimal_places=3, max_digits=3)
    tempo = models.DecimalField(decimal_places=3, max_digits=6)
    valence = models.DecimalField(decimal_places=3, max_digits=3)

    def __str__(self):
        return super(AudioFeatures, self).__str__()

#  }}} AudioFeatures #
