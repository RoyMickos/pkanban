from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter
from pkanban import views

router = DefaultRouter()
router.register(r'task', views.TaskViewSet)
router.register(r'user', views.UserViewSet)
router.register(r'phase', views.PhaseViewSet)
router.register(r'wip', views.WipViewSet)
router.register(r'valuestream', views.ValueStreamViewSet)

urlpatterns = patterns('',
  url(r'^', include(router.urls)),
  url(r'^api-auth/$', include('rest_framework.urls', namespace='rest_framework')),
)
