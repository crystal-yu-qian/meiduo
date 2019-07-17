from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^address/$',views.AddressView.as_view(),name='address'),
    url(r'^areas/$',views.AreasView.as_view(),name='areas'),
]