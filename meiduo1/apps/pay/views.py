from django import http
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
from django.views import View

from apps.orders.models import OrderInfo
from apps.pay.models import Payment
from untils.response_code import RETCODE
from alipay import AliPay
from meiduo1 import settings

class PayUrlView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        user = request.user
        try:
            order = OrderInfo.objects.get(
                user=user,
                order_id=order_id,
                status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']
            )
        except OrderInfo.DoesNotExist:
            return http.JsonResponse({'code': RETCODE.PARAMERR})

        app_private_key_string = open(settings.APP_PRIVATE_KEY_PATH).read()
        alipay_public_key_string = open(settings.ALIPAY_PUBLIC_KEY_PATH).read()
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG
        )
        subject = '美多商城'
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount),
            subject=subject,
            return_url=settings.ALIPAY_RETURN_URL,
        )
        pay_url = settings.ALIPAY_URL + '?' + order_string
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok', 'alipay_url': pay_url})
# 支付账户 adhwxh9077@sandbox.com
class PayStatusView(View):
    def get(self,request):
        data = request.GET.dict()
        signature = data.pop('sign')
        app_private_key_string = open(settings.APP_PRIVATE_KEY_PATH).read()
        alipay_public_key_string = open(settings.ALIPAY_PUBLIC_KEY_PATH).read()
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG
        )
        success = alipay.verify(data,signature)
        if success:
            trade_no = data.get('trade_no')
            out_trade_no = data.get('out_trade_no')
            Payment.objects.create(
                order_id = out_trade_no,
                trade_id = trade_no
            )
        else:
            return http.HttpResponseBadRequest('稍后查询')
        return render(request,'pay_success.html',context={'trade_no':trade_no})