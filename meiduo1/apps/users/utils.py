import re
from django.contrib.auth.backends import ModelBackend
from apps.users.models import User, Address


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
    token = s.dumps({'user_id': user_id})
    return 'http://www.meiduo.site:8000/email_active/?token=%s' % token.decode()

from itsdangerous import BadSignature,SignatureExpired
def check_verify_token(token):
    s = Serializer(settings.SECRET_KEY, expires_in=3600)
    try:
        result = s.loads(token)
    except BadSignature:
        return None
    user_id = result.get("user_id")
    return user_id


def get_addresses(request):
    login_user = request.user
    addresses = Address.objects.filter(user=login_user, is_deleted=False)
    address_dict_list = []
    for address in addresses:
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "province_id": address.province_id,
            "city": address.city.name,
            "city_id": address.city_id,
            "district": address.district.name,
            "district_id": address.district_id,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email}
        address_dict_list.append(address_dict)
    context = {
        'default_address_id': login_user.default_address_id,
        'addresses': address_dict_list,
    }
    return context