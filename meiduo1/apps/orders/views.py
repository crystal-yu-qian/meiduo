from django import http
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.goods.models import SKU
from apps.orders.models import OrderInfo, OrderGoods
from apps.users.models import Address
from django_redis import get_redis_connection

from apps.users.utils import get_addresses
from untils.response_code import RETCODE


class OrderVisitView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        user = request.user
        con = get_addresses(request)
        redis_conn = get_redis_connection('carts')
        sku_id_counts = redis_conn.hgetall('carts:%s' % user.id)
        selected_ids = redis_conn.smembers('selected:%s' % user.id)
        selected_carts = {}
        for id in selected_ids:
            selected_carts[int(id)] = int(sku_id_counts[id])
        ids = selected_carts.keys()
        skus = SKU.objects.filter(id__in=ids)
        total_count = 0
        total_amount = 0
        for sku in skus:
            sku.count = selected_carts[sku.id]
            sku.amount = selected_carts[sku.id] * sku.price
            total_count += selected_carts[sku.id]
            total_amount += selected_carts[sku.id] * sku.price
        context = {
            'addresses': con['addresses'],

            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
            'freight': 10,
            'payment_amount': total_amount + 10
        }
        return render(request, 'place_order.html', context=context)


import json


class OrderCommitView(LoginRequiredMixin, View):
    def post(self, request):
        data = json.loads(request.body.decode())
        address_id = data.get('address_id')
        pay_method = data.get('pay_method')
        if not all([address_id, pay_method]):
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '参数不全'})
        try:
            pay_method = int(pay_method)
        except Exception as e:
            pass
        user = request.user
        try:
            address = Address.objects.get(pk=address_id)
        except Address.DoesNotExist:
            pass
        from django.utils import timezone
        order_id = timezone.localtime().strftime('%Y%m%d%H%M%S') + '%09d' % user.id
        from decimal import Decimal
        total_amount = Decimal('0')
        freight = Decimal('10')
        total_count = 0
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return http.JsonResponse({'code': RETCODE.PARAMERR})
        if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH']:
            status = OrderInfo.ORDER_STATUS_ENUM['UNSEND']
        else:
            status = OrderInfo.ORDER_STATUS_ENUM['UNPAID']
        from django.db import transaction
        with transaction.atomic():
            save_point = transaction.savepoint()
            order = OrderInfo.objects.create(
                order_id=order_id,
                user=user,
                address_id=address_id,
                total_count=total_count,
                total_amount=total_amount,
                freight=freight,
                pay_method=pay_method,
                status=status
            )
        redis_conn = get_redis_connection('carts')
        sku_id_counts = redis_conn.hgetall('carts:%s' % user.id)
        selected_ids = redis_conn.smembers('selected:%s' % user.id)
        carts = {}
        for id in selected_ids:
            carts[int(id)] = int(sku_id_counts[id])
        ids = carts.keys()
        for id in ids:
            sku = SKU.objects.get(pk=id)
            count = carts[sku.id]
            if count > sku.stock:
                return http.JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': '库存不足'})
            import time
            time.sleep(10)

            # sku.stock -= count
            # sku.sales += count
            # sku.save()
            old_stock = sku.stock
            new_stock = sku.stock - count
            new_sales = sku.sales + count
            rect = SKU.objects.filter(stock=old_stock, pk=sku.id).update(stock=new_stock, sales=new_sales)
            if rect == 0:
                transaction.savepoint_rollback(save_point)
                return http.JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': '库存不足'})
            OrderGoods.objects.create(
                order=order,
                sku=sku,
                count=count,
                price=sku.price
            )
            order.total_count += count
            order.total_amount += (count * sku.price)
        order.save()
        transaction.savepoint_commit(save_point)
        redis_conn.hdel('carts:%s' % user.id, *selected_ids)
        redis_conn.srem('selected:%s' % user.id, *selected_ids)
        return http.JsonResponse(
            {'code': RETCODE.OK, 'errmsg': 'ok', 'order_id': order.order_id, 'payment_amount': order.total_amount})


class OrderSuccessView(View):
    def get(self, request):
        order_id = request.GET.get('order_id')
        payment_amount = request.GET.get('payment_amount')
        pay_method = request.GET.get('pay_method')
        context = {
            'order_id': order_id,
            'payment_amount': payment_amount,
            'pay_method': pay_method
        }
        return render(request, 'order_success.html', context=context)

class MyOrderView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        user = request.user
        page_num = request.GET.get('page_num')
        orders = user.orderinfo_set.all().order_by("-create_time")
        for order in orders:
            order_goods = order.skus.all()
            order.status_name = OrderInfo.ORDER_STATUS_CHOICES[order.status - 1][1]
            order.pay_method_name = OrderInfo.PAY_METHOD_CHOICES[order.pay_method - 1][1]
            order.sku_list = []
            for good in order_goods:
                sku = good.sku
                sku.amount = good.price * good.count
                sku.count = good.count
                order.sku_list.append(sku)
        try:
            page_num = int(page_num)
        except:
            return http.HttpResponseBadRequest('参数错误')
        try:
            paginator = Paginator(orders, 2)
            page_orders = paginator.page(page_num)
            total_page = paginator.num_pages
        except EmptyPage:
            return http.HttpResponseNotFound('订单不存在')
        #
        context = {
            "page_orders": page_orders,
            'total_page': total_page,
            'page_num': page_num,
        }
        return render(request, 'user_center_order.html', context = context)