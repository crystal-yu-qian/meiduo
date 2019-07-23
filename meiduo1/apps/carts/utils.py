import base64
import pickle
from django_redis import get_redis_connection
def merge_cookie_to_redis(request,user,response):
    cookie_carts = request.COOKIES.get('carts')
    if cookie_carts is not None:
        carts = pickle.loads(base64.b64decode(cookie_carts))
        redis_conn = get_redis_connection('carts')
        sku_id_counts = redis_conn.hgetall('carts:%s'%user.id)
        new_sku_id_count = {}
        for sku_id,count in sku_id_counts.items():
            new_sku_id_count[int(sku_id)]=int(count)
        selected_ids = []
        unselected_ids = []
        update_redis_carts ={}
        for sku_id,count_selected_dict in carts.items():
            if sku_id in new_sku_id_count:
                update_redis_carts[sku_id] = count_selected_dict['count']
            else:
                update_redis_carts[sku_id] = count_selected_dict['count']
            if count_selected_dict['selected']:
                selected_ids.append(sku_id)
            else:
                unselected_ids.append(sku_id)
        redis_conn.hmset('carts:%s'%user.id,update_redis_carts)
        if len(selected_ids)>0:
            redis_conn.sadd('selected:%s'%user.id,*selected_ids)
        if len(unselected_ids)>0:
            redis_conn.srem('selected:%s'%user.id,*unselected_ids)
        response.delete_cookie('carts')
        return response
    return response