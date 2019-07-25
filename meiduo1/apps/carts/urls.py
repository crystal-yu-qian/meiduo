from django.conf.urls import url
from apps.carts import views

urlpatterns = [
    url(r'^carts/$',views.CartsView.as_view(),name='carts'),
    url(r'^carts/selection/$',views.CartsSelectAllView.as_view(),name='carts_selected'),
    url(r'^carts/simple/$',views.CartsSimpleView.as_view(),name='carts_simple'),

]