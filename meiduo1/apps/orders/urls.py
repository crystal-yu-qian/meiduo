from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^orders/$',views.OrderVisitView.as_view(),name='order'),


]