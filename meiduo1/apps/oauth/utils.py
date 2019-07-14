from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature
from meiduo1 import settings

def generic_openid_token(openid):
    s = Serializer(secret_key=settings.SECRET_KEY,expires_in=3600)
    token = s.dumps({"openid":openid})
    return token.decode()
def check_openid_token(openid):
    s = Serializer(secret_key=settings.SECRET_KEY, expires_in=3600)
    try:
        result = s.loads(openid)
    except BadSignature:
        return None
    return result.get('openid')