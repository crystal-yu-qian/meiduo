from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.contents.models import ContentCategory
from apps.contents.until import get_categories


class IndexView(View):
    def get(self,request):
        categories = get_categories()
        contents = {}
        content_categories = ContentCategory.objects.all()
        for cat in content_categories:
            contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

        # 渲染模板的上下文
        context = {
            'categories': categories,
            'contents': contents,
        }
        return render(request,"index.html",context)

# 用于测试图片上传,shell
# #1.导入库
# from fdfs_client.client import  Fdfs_client
# #2.创建实例
# client=Fdfs_client('utils/fastdfs/client.conf')
# #3.上传图片
# # 绝对路径
# client.upload_by_filename('/home/python/Desktop/images/long.png')
