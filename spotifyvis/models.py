from django.db import models
from django.contrib.postgres.fields import JSONField

class Genre(models.Model):
    
    class Meta:
        verbose_name = "Genre"
        verbose_name_plural = "Genres"

    name = models.CharField()

    def __str__(self):
        return self.name 


class Artist(models.Model):

    class Meta:
        verbose_name = "Artist"
        verbose_name_plural = "Artists"

    name = models.CharField()
    genre = models.OneToOneField(Genre, on_delete=models.CASCADE)

    def __str__(self):
        return super(Artist, self).__str__()


class AudioFeatures(models.Model):
        
    class Meta:
        verbose_name = "AudioFeatures"
        verbose_name_plural = "AudioFeatures"

    features = JSONField()

    def __str__(self):
        return self.features


class Year(models.Model):
    
    class Meta:
        verbose_name = "Year"
        verbose_name_plural = "Years"


    year = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.year


class Track(models.Model):
    
    class Meta:
        verbose_name = "Track"
        verbose_name_plural = "Tracks"

    popularity = models.DecimalField(decimal_places=2)
    runtime = models.PositiveSmallIntegerField()
    name = models.CharField()

    def __str__(self):
        return self.name 
