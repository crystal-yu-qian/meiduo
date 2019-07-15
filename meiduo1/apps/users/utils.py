import re
from django.contrib.auth.backends import ModelBackend
from apps.users.models import User


def get_users_by_username(username):
    try:
        if re.match(r'^1[3-9]\d{9}$', username):
            user = User.objects.get(mobile=username)
        else:
            user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = None
    return user


class UsernameMobileModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = get_users_by_username(username)
        if user is not None and user.check_password(password):
            return user


from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from meiduo1 import settings


def generate_verify_email_url(user_id):
    s = Serializer(settings.SECRET_KEY, expires_in=3600)
    token = s.dumps({'openid': user_id})
    return 'http://www.meiduo.site:8000/email_active/?token=%s' % token.decode()
