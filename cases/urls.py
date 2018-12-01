from django.conf.urls import url

from . import views
app_name = 'cases'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^new/$', views.new, name='new'),
    url(r'^(?P<case_id>[0-9]+)/$', views.case_detail, name='case_detail'),
]
