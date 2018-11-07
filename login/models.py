from django.db import models

# id's are 22 in length in examples but set to 30 for buffer
MAX_ID = 30
# saw tokens being about ~150 chars in length
TOKEN_LENGTH = 200

class User(models.Model):
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    # the user's Spotify ID
    id = models.CharField(primary_key=True, max_length=MAX_ID)
    secret = models.CharField(max_length=50, default='')
    refresh_token = models.CharField(max_length=TOKEN_LENGTH)
    access_token = models.CharField(max_length=TOKEN_LENGTH)
    access_obtained_at = models.DateTimeField(auto_now=True)
    access_expires_in = models.PositiveIntegerField()

    def __str__(self):
        return self.id

class HistoryUpload(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    document = models.FileField(upload_to='history/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
