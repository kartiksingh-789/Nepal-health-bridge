from .models import User

def session_user(request):
    """
    Makes 'session_user' available in every template automatically.
    Use {{ session_user }} in templates instead of {{ request.user }}
    """
    mobile = request.session.get('user_mobile')
    if mobile:
        try:
            user = User.objects.get(mobile=mobile)
            return {'session_user': user}
        except User.DoesNotExist:
            pass
    return {'session_user': None}