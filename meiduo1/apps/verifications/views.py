from django.shortcuts import render

# Create your views here.
from django.views import View
from django.http import HttpResponse,JsonResponse
from django_redis import get_redis_connection
from libs.captcha.captcha import captcha
from django import http

from libs.yuntongxun.sms import CCP


class ImgCodeView(View):
    def get(self,request,uuid):
        code,image = captcha.generate_captcha()
        coon = get_redis_connection('code')
        coon.setex('img:%s'%uuid,120,code)
        return HttpResponse(image,content_type="image/jpeg")

# 上面为图片验证码,下面为短信验证码

from untils.response_code import RETCODE
import logging
logger = logging.getLogger("django")
class SmsView(View):
    def get(self,request,mobile):
        img_code = request.GET.get("image_code")
        uuid = request.GET.get('image_code_id')
        if not all([img_code,uuid]):
            return HttpResponse('参数不全')
        try:
            coon = get_redis_connection('code')
            redis_code = coon.get('img:%s'%uuid)
            if redis_code is None:
                return HttpResponse('图片验证码过期')
            if redis_code.decode().lower() != img_code.lower():
                return HttpResponse("验证码不一致")
            coon.delete('img:%s'%uuid)
            send_flag = coon.get('send_flag:%s'%mobile)
            if send_flag:
                # print('1111')
                return JsonResponse({'code':RETCODE.THROTTLINGERR,'errmsg':"操作过于频繁"})
        except Exception as e:
            logger.error(e)
            return http.HttpResponseBadRequest('redis连接错误')
        from random import randint
        sms_code = '%06d'%randint(0,999999)
        pl = coon.pipeline()
        pl.setex('sms:%s'%mobile,300,sms_code)
        pl.setex('send_flag:%s'%mobile,300,1)
        pl.execute()
        CCP().send_template_sms(mobile, [sms_code, 5], 1)
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '发送短信成功'})

