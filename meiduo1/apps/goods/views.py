from django import http
from django.shortcuts import render

# Create your views here.
from django.views import View
from untils.response_code import RETCODE

from apps.goods.models import GoodsCategory, SKU
from apps.goods.utils import get_breadcrumb


class ListView(View):
    def get(self,request,category_id,page_num):
        try:
            category=GoodsCategory.objects.get(pk=category_id)
        except GoodsCategory.DoesNotExist:
            return render(request,'404.html')
        breadcrumb = get_breadcrumb(category)

        sort = request.GET.get('sort')
        if sort == 'default':
            sort_field = 'create_time'
        elif sort == 'price':
            sort_field = 'price'
        else:
            sort_field = 'sales'
            sort = 'hot'
        skus = SKU.objects.filter(category=category).order_by(sort_field)
        from django.core.paginator import Paginator
        try :
            paginator = Paginator(skus,5)
            pages_sku = paginator.page(page_num)
            total_pages = paginator.num_pages
        except Exception as e:
            return render(request,'404.html')
        context = {
            "breadcrumb":breadcrumb,
            'sort':sort,
            'category':category,
            'page_skus':pages_sku,
            'total_page':total_pages,
            'page_num':page_num,
        }
        return render(request,"list.html",context=context)

class HotView(View):
    def get(self,request,category_id):
        try:
            category=GoodsCategory.objects.get(pk=category_id)
        except GoodsCategory.DoesNotExist:
            return http.JsonResponse({'code':RETCODE.NODATAERR,'errmsg':"没有此分类"})
        skus = SKU.objects.filter(category_id=category_id).order_by('-sales')[:2]
        skus_list = []
        for sku in skus:
            skus_list.append({
                'id':sku.id,
                'name':sku.name,
                'price':sku.price,
                'default_image_url':sku.default_image.url
            })
        return http.JsonResponse({'code':RETCODE.OK,'errmsg':'ok','hot_skus':skus_list})