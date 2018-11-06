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
    # TODO: pass back user id as well?
    pass

