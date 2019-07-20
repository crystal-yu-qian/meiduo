import json

from django import http
from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.contents.until import get_categories
from untils.response_code import RETCODE

from apps.goods.models import GoodsCategory, SKU, GoodsVisitCount
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


class DetailView(View):
    def get(self, request, sku_id):

        # 获取当前sku的信息
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return render(request, '404.html')

        # 查询商品频道分类
        categories = get_categories()
        # 查询面包屑导航
        breadcrumb = get_breadcrumb(sku.category)

        # 构建当前商品的规格键
        sku_specs = sku.specs.order_by('spec_id')
        sku_key = []
        for spec in sku_specs:
            sku_key.append(spec.option.id)
        # 获取当前商品的所有SKU
        skus = sku.spu.sku_set.all()
        # 构建不同规格参数（选项）的sku字典
        spec_sku_map = {}
        for s in skus:
            # 获取sku的规格参数
            s_specs = s.specs.order_by('spec_id')
            # 用于形成规格参数-sku字典的键
            key = []
            for spec in s_specs:
                key.append(spec.option.id)
            # 向规格参数-sku字典添加记录
            spec_sku_map[tuple(key)] = s.id
        # 获取当前商品的规格信息
        goods_specs = sku.spu.specs.order_by('id')
        # 若当前sku的规格信息不完整，则不再继续
        if len(sku_key) < len(goods_specs):
            return
        for index, spec in enumerate(goods_specs):
            # 复制当前sku的规格键
            key = sku_key[:]
            # 该规格的选项
            spec_options = spec.options.all()
            for option in spec_options:
                # 在规格参数sku字典中查找符合当前规格的sku
                key[index] = option.id
                option.sku_id = spec_sku_map.get(tuple(key))
            spec.spec_options = spec_options

        # 渲染页面
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
            'specs': goods_specs,
        }

        return render(request, 'detail.html', context)


class VisitView(View):
    def post(self,request):
        data = json.loads(request.body.decode())
        catagory_id = data.get('category_id')
        try:
            catagory = GoodsCategory.objects.get(pk=catagory_id)
        except Exception as e:
            return http.JsonResponse({'code':RETCODE.NODATAERR,'errmsg':'没有此分类'})
        from django.utils import timezone
        today = timezone.localdate()
        try:
            gvc = GoodsVisitCount.objects.get(category=catagory,date=today)
        except GoodsVisitCount.DoesNotExist:
            GoodsVisitCount.objects.create(category=catagory,date=today,count=1)
        else:
            gvc.count+=1
            gvc.save()
            return http.JsonResponse({'code':RETCODE.OK,'errmsg':'ok'})