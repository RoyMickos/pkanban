from django.conf.urls import patterns, include, url
#from django.conf.urls.defaults import *
from django.conf.urls import *
from models import PkTask
from views import *
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    #url(r'^$', show_board),
    #url(r'^$', show_spa),
    url(r'^$', load_app),
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'pkanban/login.html'}),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', {'login_url': '/pkanban/login/?next=/pkanban/'}),
    url(r'^streams/', editBoard),
    url(r'^nphase/', newPhase),
    url(r'^nstream/', newStream),
)
