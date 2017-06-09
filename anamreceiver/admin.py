#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from django.contrib import admin

from anamreceiver.models import Collect


class HamedAdminSite(admin.AdminSite):
    site_header = "ANAM receiver"

admin_site = HamedAdminSite(name='anamadmin')


@admin.register(Collect, site=admin_site)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ('id', 'started_on', 'imported', 'images_copied')
