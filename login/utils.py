from .models import User

def get_user_context(user_obj):
    """Get context for rendering with User's ID and secret.

    :user_obj: User object to make context for.
    :returns: context to pass back to HTML file.

    """
    return { 'user_id': user_obj.id, 'user_secret': user_obj.secret, }
