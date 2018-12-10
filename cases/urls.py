from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'cases'
urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^index/$', views.index, name='index'),
    url(r'^new/$', login_required(views.CaseCreateView.as_view()), name='new'),
    url(r'^rules/new$', views.new_rule, name='new_rule'),
    url(r'^rules/index', views.rule_index, name='rule_index'),
    url(r'^(?P<case_id>[0-9]+)/$', views.case_detail, name='case_detail'),
    url(r'^api/get_case_and_alert/$', views.get_case_and_alert, name='get_case_and_alert'),
]
