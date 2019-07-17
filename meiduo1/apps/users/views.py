from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect

# Create your views here.
from django.views import View
import re
from django import http
from django.http import HttpResponse
from apps.users.models import User, Address

from django.urls import reverse
from django.contrib.auth import login, logout


class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')

        if not all([username, password, password2, mobile]):
            return http.HttpResponseBadRequest('参数不全')
        if not re.match(r"^[a-zA-Z0-9]{5,20}$", username):
            return http.HttpResponseBadRequest('请输入字符5-20的用户名')
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseBadRequest('请输入8-20位的密码')
        if password2 != password:
            return http.HttpResponseBadRequest('两次输入的密码不一致')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseBadRequest('手机号不符合规则')

        user = User.objects.create_user(username=username, password=password, mobile=mobile)
        login(request, user)
        path = reverse('contents:index')
        response = redirect(path)
        return response


class UsernameCountView(View):
    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        return http.JsonResponse({'count': count})


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        remembered = request.POST.get('remembered')
        next = request.GET.get('next')

        if not all([username, password]):
            return http.HttpResponseBadRequest('参数不全')
        if not re.match(r"^[a-zA-Z0-9]{5,20}$", username):
            return http.HttpResponseBadRequest('请输入字符5-20的用户名')
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseBadRequest('请输入8-20位的密码')
        from django.contrib.auth import authenticate
        user = authenticate(username=username, password=password)
        if user is None:
            return http.HttpResponseBadRequest('账号或密码错误')

        login(request, user)
        if remembered == "on":
            request.session.set_expiry(None)
        else:
            request.session.set_expiry(0)
        if next:
            responce = redirect(next)
        else:
            responce = redirect(reverse('contents:index'))
        responce.set_cookie('username', user.username)
        return responce


class LogoutView(View):
    def get(self, request):
        logout(request)
        responce = redirect(reverse('contents:index'))
        responce.delete_cookie('username')
        return responce


class UserInfoView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        context = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active
        }
        return render(request, 'user_center_info.html', context=context)


import json
from untils.response_code import RETCODE


# from django.core.mail import send_mail
# from meiduo1 import settings

class EmailView(View):
    def put(self, request):
        user = request.user
        body = request.body
        data = json.loads(body.decode())
        email = data.get('email')
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.JsonResponse({'code': RETCODE.PARAMERR, "errmsg": '邮箱格式不正确'})
        try:
            user.email = email
            user.save()
        except Exception as e:
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '保存失败'})

        # subject = '美多商场激活邮件'
        # message = '成功'
        # from_email = settings.EMAIL_FROM
        # recipient_list = [email]
        # html_message = '<a href="#">点击激活</a>'
        # send_mail(subject, message, from_email, recipient_list,html_message=html_message)
        from celery_tasks.email.tasks import send_active_email
        send_active_email.delay(email, request.user.id)

        return http.JsonResponse({'code': RETCODE.OK})


# celery -A celery_tasks.main worker -l info

from apps.users.utils import check_verify_token


class EmailActiveView(View):
    def get(self, request):
        token = request.GET.get("token")
        if token is None:
            return http.HttpResponseBadRequest('缺少参数')
        user_id = check_verify_token(token)
        if user_id is None:
            return http.HttpResponseBadRequest('参数错误')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return http.HttpResponseBadRequest('没有此用户')
        user.email_active = True
        user.save()
        return redirect(reverse('users:center'))


import logging

logger = logging.getLogger('django')


class CreateAddressViw(View):
    def post(self, request):
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseBadRequest('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseBadRequest('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseBadRequest('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseBadRequest('参数email有误')
        try:
            address = Address.objects.create(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email)
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '新增地址失败'})
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email}
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '新增地址成功', 'address': address_dict})


class UpdateAdressView(View):
    def put(self, request, address_id):
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseBadRequest('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseBadRequest('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseBadRequest('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseBadRequest('参数email有误')
        try:
            result = Address.objects.filter(pk=address_id).update(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email)
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '修改地址失败'})
        if result == 0:
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '修改地址失败'})
        address = Address.objects.get(pk=address_id)
        update_data = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email}
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '修改地址成功', 'address': update_data})
    def delete(self,request,address_id):
        try:
            address = Address.objects.get(pk=address_id)
            address.is_deleted=True
            address.save()
        except Address.DoesNotExist:
            return http.JsonResponse({'code':RETCODE.NODATAERR,'errmsg':'没有此记录'})
        return http.JsonResponse({'code':RETCODE.OK,'errmsg':'ok'})