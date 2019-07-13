import re
from django.contrib.auth.backends import ModelBackend
from apps.users.models import User


def get_users_by_username(username):
    try:
        if re.match(r'^1[3-9]\d{9}$',username):
            user = User.objects.get(mobile=username)
        else:
            user = User.objects.get(username=username)
    except User.DoesNotExist:
        user= None
    return user
class UsernameMobileModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = get_users_by_username(username)
        if user is not None and user.check_password(password):
            return user
