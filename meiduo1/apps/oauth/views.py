from django import http
from django.contrib.auth import login
from django.shortcuts import render,redirect

# Create your views here.
from QQLoginTool.QQtool import OAuthQQ
from django.urls import reverse
from django.views import View
from meiduo1 import settings
from apps.oauth.models import OauthQQUser
from apps.users.models import User
from apps.oauth.utils import generic_openid_token,check_openid_token

class OauthQQLoginView(View):
    def get(self,request):
        state = 'test'
        qq = OAuthQQ(client_id = settings.QQ_CLIENT_ID,
                     client_secret=settings.QQ_CLIENT_SECRET,
                     redirect_uri=settings.QQ_REDIRECT_URI,
                     state=state)
        login_url = qq.get_qq_url()
        return http.JsonResponse({"login_url": login_url})

class OautnQQUserView(View):
    def get(self,request):
        code = request.GET.get('code')
        state = request.GET.get('state')
        if code is None:
            return http.HttpResponseBadRequest('参数有误')
        qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                     client_secret=settings.QQ_CLIENT_SECRET,
                     redirect_uri=settings.QQ_REDIRECT_URI,
                     state=state)
        token = qq.get_access_token(code)
        openid = qq.get_open_id(token)
        try:
            qquser = OauthQQUser.objects.get(openid=openid)
        except OauthQQUser.DoesNotExist:

            token = generic_openid_token(openid)
            return render(request,'oauth_callback.html',context={"openid":token})
        else:
            login(request,qquser.user)
            responce = redirect(reverse("contents:index"))
            responce.set_cookie('username',qquser.user.username)
            return responce
    def post(self,request):
        mobile = request.POST.get('mobile')
        password = request.POST.get('pwd')
        sms_code = request.POST.get('sms_code')
        openid = request.POST.get('openid')

        openid= check_openid_token(openid)
        if openid is None:
            return http.HttpResponseBadRequest('数据被篡改')
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            user = User.objects.create_user(username= mobile,password= password,mobile= mobile)
        else:
            if not user.check_password(password):
                return http.HttpResponseBadRequest('绑定失败')
        OauthQQUser.objects.create(user= user,openid=openid)
        login(request,user)
        responce = redirect(reverse("contents:index"))
        responce.set_cookie('username',user.username)
        return responce


