from django.conf.urls import patterns, include, url
from django.conf.urls.defaults import *
from models import PkTask
from views import *
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    #url(r'^$', show_board),
    url(r'^$', show_spa),
    #url(r'^Newban/', show_spa),
    # task view below needs to be rewritten
    #url(r'^Task/(?P<object_id>\d+)/$', object_detail, 
    #    {'queryset': PkTask.objects.all()}, name="task_view"),
    url(r'^Task/(?P<object_id>\d+)/$', viewTask, name="task_view"),
    url(r'^Task/NewTask/$', addTask),
    url(r'^Description/(?P<object_id>\d+)/$', getDescription),
    url(r'^wip/', getWip), # ajax response
    url(r'^backlog/', getBacklog), # ajax response
    url(r'^streams/', editBoard),
    url(r'^nphase/', newPhase),
    url(r'^nstream/', newStream),
    url(r'^advance/', advanceTask),
    url(r'^archive/', showArchive),
    url(r'^effort/', addEffort),
    url(r'^delete/', speedyArchieve),
    #url(r'^Tests/', run_tests),
)
