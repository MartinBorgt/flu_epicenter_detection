from django.conf.urls import include, url
from django.views.generic import ListView, DetailView,  TemplateView

from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^contact/', views.contact, name='contact'),

    url(r'^flumap/$', views.flumap, name='flu map'),

    url(r'^flumap/(?P<functioncalled>[-\w]+)/$', views.flumap, name='flu map'),

]
