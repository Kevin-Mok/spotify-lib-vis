from django.contrib import admin
from .models import Track, Artist, AudioFeatures, User, Genre

# Register your models here.
admin.site.register(Track)
admin.site.register(Artist)
admin.site.register(AudioFeatures)
admin.site.register(User)
admin.site.register(Genre)
