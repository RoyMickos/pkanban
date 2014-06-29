from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter
from pkanban import views

router = DefaultRouter()
router.register(r'task', views.TaskViewSet)
router.register(r'user', views.UserViewSet)

urlpatterns = patterns('',
  url(r'^', include(router.urls)),
  url(r'^api-auth/$', include('rest_framework.urls', namespace='rest_framework')),
)
