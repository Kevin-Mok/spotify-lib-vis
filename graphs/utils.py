def get_secret_context(user_secret):
    """Return user_secret in context for graph pages.

    :user_secret: User secret to put in context.
    :returns: context with user secret.

    """
    return { 'user_secret': user_secret, }
