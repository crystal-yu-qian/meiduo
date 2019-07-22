import json

from django import http
from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.goods.models import SKU
from untils.response_code import RETCODE


class CartsView(View):
    def post(self,request):
        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')
        count = data.get('count')
        selected = data.get('selected',True)
        if not all([sku_id,count]):
            return http.JsonResponse({'code':RETCODE.PARAMERR,'errmsg':'参数错误'})
        try:
            sku = SKU.objects.get(pk=sku_id)
        except SKU.DoesNotExist:
            return http.JsonResponse({'code':RETCODE.NODATAERR,'errmsg':'没有此类商品'})
        try:
            count = int('count')
        except Exception as e:
            count = 1
        user = request.user
        from django_redis import get_redis_connection
        if user is not None and user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            redis_conn.hset('carts:%s'%user.id,sku_id,count)
            redis_conn.sadd('selected:',sku_id)
            return http.JsonResponse({'code':RETCODE.OK,'errmsg':"ok"})
        else:
            carts ={}
            carts[sku_id] = {
                'count': count,
                'selected': selected
            }
            import pickle
            import base64
            d = pickle.dumps(carts)
            en = base64.b64encode(d)
            response = http.JsonResponse({'code':RETCODE.OK,'errmsg':"ok"})
            response.set_cookie('carts',en,max_age=3600)
            return response
