from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^register/$',views.RegisterView.as_view(),name='register'),
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UsernameCountView.as_view(),name='usernamecount'),
    url(r'^login/$',views.LoginView.as_view(),name='login'),
    url(r'^logout/$',views.LogoutView.as_view(),name='logout'),
    url(r'^center/$', views.UserInfoView.as_view(), name='center'),
    url(r'^emails/$',views.EmailView.as_view(),name='email'),
    url(r'^email_active/$',views.EmailActiveView.as_view(),name='email_active'),

    url(r'^addresses/create/$',views.CreateAddressViw.as_view(), name='create_address'),
    url(r'^addresses/(?P<address_id>\d+)/$',views.UpdateAdressView.as_view(),name='update_address'),
    url(r'^addresses/(?P<address_id>\d+)/default/$',views.DefaultAddressView.as_view(),name='default_address'),
    url(r'^addresses/(?P<address_id>\d+)/title/$',views.UpdateTitleAddressView.as_view(),name='update_title'),
    url(r'^password/$',views.ChangePasswordView.as_view(),name='change_pass'),

]
    
