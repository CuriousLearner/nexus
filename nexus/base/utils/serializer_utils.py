def _get_user_from_context(context):
    if 'user' in context:
        return context['user']
    if 'request' in context:
        return context['request'].user
    return None
