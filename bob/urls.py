from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'bob.views.home', name='home'),
    # url(r'^bob/', include('bob.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    (r'^rankings$', 'scoring.views.rankings'),
    (r'^matchlist$', 'scoring.views.matchlist'),
    (r'^matchlist_generate$', 'scoring.views.matchlist_generate'),
    (r'^matchlist_import$', 'scoring.views.matchlist_import'),
    (r'^edit_match/(.*)$', 'scoring.views.edit_match'),
    (r'^edit_match_scoring/(\d+)/(.*)$', 'scoring.views.edit_match_scoring'),
    (r'^$', 'scoring.views.homepage'),
   
)

urlpatterns += staticfiles_urlpatterns()