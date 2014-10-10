from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'heroku.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^pkanban/', include('pkanban.app_urls')),
    url(r'^pk/', include('pkanban.rest_urls')),
    url(r'^admin/', include(admin.site.urls)),
)
