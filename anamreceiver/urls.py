#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from django.conf.urls import url

from anamreceiver import views
from anamreceiver.admin import admin_site

urlpatterns = [
    url(r'^$', views.home, name='home'),

    url(r'^api/upload/?$', views.api_upload, name='api_upload'),

    url(r'^api/collects/(?P<collect_id>[0-9]+)/archive/?$',
        views.archive, name='api_collect_archive'),
    url(r'^api/collects/(?P<collect_id>[0-9]+)/unarchive/?$',
        views.unarchive, name='api_collect_unarchive'),

    url(r'^api/collects/(?P<collect_id>[0-9]+)/mark_imported/?$',
        views.mark_imported, name='api_collect_mark_imported'),
    url(r'^api/collects/(?P<collect_id>[0-9]+)/mark_images_copied/?$',
        views.mark_images_copied, name='api_collect_mark_images_copied'),

    url(r'^api/collects/(?P<collect_id>[0-9]+)/?$',
        views.single_collect, name='api_collect'),
    url(r'^api/collects/?$', views.all_collects, name='api_collects'),
    url(r'^api/check/?$', views.check, name='api_check'),

    url(r'^admin/', admin_site.urls),
]

from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
