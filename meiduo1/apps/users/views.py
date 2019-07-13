from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render,redirect

# Create your views here.
from django.views import View
import re
from django import http
from django.http import HttpResponse
from apps.users.models import User

from django.urls import reverse
from django.contrib.auth import login, logout


class RegisterView(View):
    def get(self,request):
        return render(request,'register.html')
    def post(self,request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')

        if not all([username,password,password2,mobile]):
            return http.HttpResponseBadRequest('参数不全')
        if not re.match(r"^[a-zA-Z0-9]{5,20}$",username):
            return http.HttpResponseBadRequest('请输入字符5-20的用户名')
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseBadRequest('请输入8-20位的密码')
        if password2!=password:
            return http.HttpResponseBadRequest('两次输入的密码不一致')
        if not re.match(r'^1[3-9]\d{9}$',mobile):
            return http.HttpResponseBadRequest('手机号不符合规则')

        user = User.objects.create_user(username=username,password=password,mobile=mobile)
        login(request,user)
        path = reverse('contents:index')
        response = redirect(path)
        return response

class UsernameCountView(View):
    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        return http.JsonResponse({'count': count})


class LoginView(View):
    def get(self,request):
        return render(request,'login.html')
    def post(self,request):
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        remembered = request.POST.get('remembered')
        next = request.GET.get('next')

        if not all([username,password]):
            return http.HttpResponseBadRequest('参数不全')
        if not re.match(r"^[a-zA-Z0-9]{5,20}$",username):
            return http.HttpResponseBadRequest('请输入字符5-20的用户名')
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseBadRequest('请输入8-20位的密码')
        from django.contrib.auth import authenticate
        user = authenticate(username=username,password=password)
        if user is None:
            return http.HttpResponseBadRequest('账号或密码错误')

        login(request,user)
        if remembered == "on":
            request.session.set_expiry(None)
        else:
            request.session.set_expiry(0)
        if next:
            responce = redirect(next)
        else:
            responce = redirect(reverse('contents:index'))
        responce.set_cookie('username',user.username)
        return responce


class LogoutView(View):
    def get(self,request):
        logout(request)
        responce = redirect(reverse('contents:index'))
        responce.delete_cookie('username')
        return responce

class UserInfoView(LoginRequiredMixin,View):
    login_url = '/login/'
    def get(self,request):
        return render(request,'user_center_info.html')