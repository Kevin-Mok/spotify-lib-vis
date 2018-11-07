import django_tables2 as tables

from pprint import pprint
from login.models import User
from api.models import History

class HistoryTable(tables.Table):
    class Meta:
        model = History
        template_name = 'django_tables2/bootstrap.html'

    iso_timestamp = tables.Column(accessor='get_iso_timestamp', orderable=False)
    track_name = tables.Column(accessor='track.name', orderable=False)
    track_id = tables.Column(accessor='track.id', orderable=False)
    artists = tables.Column(accessor='get_artists', orderable=False)

def get_secret_context(user_secret):
    """Return user_secret in context for graph pages.

    :user_secret: User secret to put in context.
    :returns: context with user secret.

    """
    return { 'user_secret': user_secret, }
