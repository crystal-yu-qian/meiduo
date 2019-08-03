from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^orders/$',views.OrderVisitView.as_view(),name='order'),
    url(r'^orders/commit/$',views.OrderCommitView.as_view(),name='commit'),
    url(r'^orders/success/$',views.OrderSuccessView.as_view(),name='success'),
    url(r'^orders/info/(?P<page_num>\d+)/$', views.MyOrderView.as_view(), name = 'my_orders'),
]