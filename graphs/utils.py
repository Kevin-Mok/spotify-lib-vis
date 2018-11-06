import django_tables2 as tables

from pprint import pprint
from login.models import User
from api.models import History

class HistoryTable(tables.Table):
    class Meta:
        model = History
        template_name = 'django_tables2/bootstrap.html'

def get_secret_context(user_secret):
    """Return user_secret in context for graph pages.

    :user_secret: User secret to put in context.
    :returns: context with user secret.

    """
    return { 'user_secret': user_secret, }


def get_user_history(user_secret):
    """Return all stored history for corresponding User to user_secret.

    :user_secret: User secret to get history for.
    :returns: list of lists of song history plus information.

    """
    user_id = get_user_id_from_secret(user_secret)
    history_fields = [field.name for field in History._meta.get_fields()]
    user_history = History.objects.filter(user__exact=user_id).order_by('-timestamp')
    user_history_table = HistoryTable(user_history)
    return { 'user_id': user_id, 
            'history_fields': history_fields,
            'user_history_table': user_history_table, }

def get_user_id_from_secret(user_secret):
    """Retrieve corresponding user_id for user_secret.

    :user_secret:
    :returns: user_id

    """
    return User.objects.get(secret=user_secret).id
