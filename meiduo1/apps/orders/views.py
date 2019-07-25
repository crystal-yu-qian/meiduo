from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.goods.models import SKU
from apps.users.models import Address
from django_redis import get_redis_connection

from apps.users.utils import get_addresses


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
