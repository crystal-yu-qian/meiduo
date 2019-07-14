from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^qq/login/$', views.OauthQQLoginView.as_view()),
    url(r'^oauth_callback/$', views.OautnQQUserView.as_view()),
]