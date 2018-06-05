from django.db import models


class Artist(models.Model):
    class Meta:
        verbose_name = "Artist"
        verbose_name_plural = "Artists"

    artist_id = models.CharField(primary_key=True, max_length=30)
    # unique since only storing one genre per artist right now
    name = models.CharField(unique=True, max_length=50)
    genre = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class User(models.Model):
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    user_id = models.CharField(primary_key=True, max_length=30)  # the user's Spotify ID
    user_name = models.CharField(max_length=30, blank=True)  # User's Spotify user name, if set

    def __str__(self):
        return self.user_name


class Track(models.Model):
    
    class Meta:
        verbose_name = "Track"
        verbose_name_plural = "Tracks"

    track_id = models.CharField(max_length=30)
    artists = models.ManyToManyField(Artist)
    year = models.PositiveSmallIntegerField()
    popularity = models.DecimalField(decimal_places=2, max_digits=2)
    runtime = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=75)
    users = models.ManyToManyField(User)

    def __str__(self):
        return self.name 


class AudioFeatures(models.Model):
        
    class Meta:
        verbose_name = "AudioFeatures"
        verbose_name_plural = "AudioFeatures"

    track = models.OneToOneField(Track, on_delete=models.CASCADE, primary_key=True,)
    danceability = models.DecimalField(decimal_places=2, max_digits=2)
    energy = models.DecimalField(decimal_places=2, max_digits=2)
    loudness = models.DecimalField(decimal_places=2, max_digits=2)
    speechiness = models.DecimalField(decimal_places=2, max_digits=2)
    acousticness = models.DecimalField(decimal_places=2, max_digits=2)
    instrumentalness = models.DecimalField(decimal_places=2, max_digits=2)
    valence = models.DecimalField(decimal_places=2, max_digits=2)
    tempo = models.DecimalField(decimal_places=2, max_digits=2)

    def __str__(self):
        return super(AudioFeatures, self).__str__()
