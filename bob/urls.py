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

    (r'^admin_controls$', 'scoring.views.admin'),
    (r'^rankings$', 'scoring.views.rankings'),
    # (r'^rankings_print$', 'scoring.views.rankings_print'),
    (r'^matchlist$', 'scoring.views.matchlist'),
    (r'^matchlist_print$', 'scoring.views.matchlist_print'),
    (r'^matchlist_generate$', 'scoring.views.matchlist_generate'),
    (r'^matchlist_import$', 'scoring.views.matchlist_import'),
    (r'^json_matchlist$','scoring.views.json_matchlist'),
    (r'^json_rankings$', 'scoring.views.json_rankings'),
    (r'^tv_display$', 'scoring.views.tv_display'),
    (r'^finals_bracket$', 'scoring.views.finals_bracket'),
    (r'^edit_match/(.*)$', 'scoring.views.edit_match'),
    (r'^edit_match_scoring/(\d+)/(.*)$', 'scoring.views.edit_match_scoring'),
    (r'^view_match_scoring_json/(\d+)/(.*)$', 'scoring.views.view_match_scoring_json'),
    (r'^edit_alliances$', 'scoring.views.edit_alliances'),
    (r'^first_matchlist$', 'scoring.views.first_matchlist'),
    (r'^first_rankings$', 'scoring.views.first_rankings'),
    (r'^$', 'scoring.views.homepage'),
   
)

urlpatterns += staticfiles_urlpatterns()