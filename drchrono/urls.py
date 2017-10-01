from django.conf.urls import include, url
from django.views.generic import TemplateView

import views

from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='home'),
    url(r'^flumap/', include('flumap.urls')),

    url(r'', include('social.apps.django_app.urls', namespace='social')),

    url(r'^admin/', include(admin.site.urls)),
]
