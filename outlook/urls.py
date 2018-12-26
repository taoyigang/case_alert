from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'outlook'
urlpatterns = [
	url(r'^$', views.home, name='home'),
	url(r'^gettoken/$', views.gettoken, name='gettoken'),
	url(r'^events/$', views.events, name='events'),
	url(r'^new/$', views.new_outlook_key, name='new_outlook_key'),
	url(r'^tutorial/$', views.tutorial, name='tutorial'),
	url(r'^index/$', views.key_index, name='key_index'),
	url(r'^delete/(?P<pk>\d+)/$', login_required(views.KeyDelete.as_view()), name='key_delete'),
]
