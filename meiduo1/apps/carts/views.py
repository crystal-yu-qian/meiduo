import json

from django import http
from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.goods.models import SKU
from untils.response_code import RETCODE
from django_redis import get_redis_connection
import pickle
import base64


class CartsView(View):
    def post(self, request):
        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')
        count = data.get('count')
        selected = data.get('selected', True)
        if not all([sku_id, count]):
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '参数错误'})
        try:
            sku = SKU.objects.get(pk=sku_id)
        except SKU.DoesNotExist:
            return http.JsonResponse({'code': RETCODE.NODATAERR, 'errmsg': '没有此类商品'})
        try:
            count = int('count')
        except Exception as e:
            count = 1
        user = request.user

        if user is not None and user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            redis_conn.hset('carts:%s' % user.id, sku_id, count)
            redis_conn.sadd('selected:', sku_id)
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': "ok"})
        else:
            carts_cookie = request.COOKIES.get('carts')
            if carts_cookie is not None:
                de = base64.b64decode(carts_cookie)
                carts = pickle.loads(de)
            else:
                carts = {}
            if sku_id in carts:
                origin_count = carts[sku_id]['count']
                count += origin_count
            carts[sku_id] = {
                'count': count,
                'selected': selected
            }

            d = pickle.dumps(carts)
            en = base64.b64encode(d)
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': "ok"})
            response.set_cookie('carts', en, max_age=3600)
            return response



    def get(self,request):
        user = request.user
        if user is not None and user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            sku_ids = redis_conn.hgetall('carts:%s'%user.id)
            selected_ids = redis_conn.smembers('selected:%s'%user.id)
            carts = {}
            for sku_id,count in sku_ids.items():
                selected = True
            else:
                selected = False
            carts[sku_id]={
                'count':count,
                'selected':sku_id in selected_ids
            }
        else:
            carts_cookie = request.COOKIES.get('carts')
            if carts_cookie is not None:
                de = base64.b64decode(carts_cookie)
                carts = pickle.loads(de)
            else:
                carts = {}
        ids = carts.keys()
        sku_list = []
        for id in ids:
            sku = SKU.objects.get(pk = id)
            sku_list.append({
                'id': sku.id,
                'name': sku.name,
                'count': carts.get(sku.id).get('count'),
                'selected': str(carts.get(sku.id).get('selected')),  # 将True，转'True'，方便json解析
                'default_image_url': sku.default_image.url,
                'price': str(sku.price),  # 从Decimal('10.2')中取出'10.2'，方便json解析
                'amount': str(sku.price * carts.get(sku.id).get('count')),
            })
        context = {
            'cart_skus':sku_list
        }
        return render(request,'cart.html',context=context)
