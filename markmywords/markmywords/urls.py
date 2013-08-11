from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'markmywords.views.home', name='home'),
    # url(r'^markmywords/', include('markmywords.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),


    # Routing to the index page
    url(r'^$', 'markmywords.views.index', name='index'),
    url(r'^authorize', 'markmywords.views.authorize', name='authorize'),
    url(r'^goal/(?P<goal_id>\d+)/$', 'markmywords.views.goals', name='goals'),
    url(r'^update/goal/(?P<goal_id>\d+)/$', 'markmywords.views.update_goal_info', name='update_goal'),
    url(r'^paypal', 'markmywords.views.paypal', name='paypal'),
    url(r'^ppsupport', 'markmywords.views.ppsupport', name='ppsupport'),
    url(r'^completedsupport', 'markmywords.views.completedsupport', name='completedsupport'),
    url(r'^support/(?P<goal_id>\d+)/$', 'markmywords.views.support', name='support'),

)
