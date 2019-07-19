from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.goods.models import GoodsCategory
from apps.goods.utils import get_breadcrumb


class ListView(View):
    def get(self,request,category_id):
        try:
            category=GoodsCategory.objects.get(pk=category_id)
        except GoodsCategory.DoesNotExist:
            return render(request,'404.html')
        breadcrumb = get_breadcrumb(category)
        context = {
            "breadcrumb":breadcrumb
        }
        return render(request,"list.html",context=context)