from django.conf.urls.defaults import patterns, include, url
import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'views.index', name='index'),
    url(r'^projects$', 'views.projects', name='projects'),
    url(r'^groups$', 'views.groups', name='groups'),
    url(r'^persons$', 'views.persons', name='persons'),
    url(r'^group/(?P<URI>http.+)$', 'views.group', name='group'),
    url(r'^person/(?P<URI>http.+)$', 'views.person', name='person'),
    # url(r'^vivolite/', include('vivolite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
