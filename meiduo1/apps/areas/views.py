from django import http
from django.core.cache import cache
from django.shortcuts import render

# Create your views here.
from django.views import View


from apps.areas.models import Area
from apps.users.models import Address
from untils.response_code import RETCODE


class AreasView(View):
    def get(self,request):
        parent_id = request.GET.get('area_id')
        if parent_id is None:
            pro_list = cache.get('pro')
            if pro_list is None:
                provinces = Area.objects.filter(parent__isnull=True)
                pro_list = []
                for pro in provinces:
                    pro_list.append({'id':pro.id,'name':pro.name})
                cache.set('pro',pro_list,24*3600)
            return http.JsonResponse({'code':RETCODE.OK,'province_list':pro_list})
        else:
            dis_list = cache.get('dis:%s'%parent_id)
            if dis_list is None:
                dist = Area.objects.filter(parent_id = parent_id)
                dis_list = []
                for dis in dist:
                    dis_list.append({'id': dis.id, 'name': dis.name})
                cache.set('dis:%s'%parent_id, dis_list, 24 * 3600)
            return http.JsonResponse({'code': RETCODE.OK, 'subs': dis_list})