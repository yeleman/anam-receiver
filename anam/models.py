#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import logging

from django.db import models
from jsonfield.fields import JSONField

logger = logging.getLogger(__name__)


class Collect(models.Model):

    started_on = models.DateTimeField(auto_now_add=True)
    dataset = JSONField(default=[], blank=True)

    @property
    def nb_submissions(self):
        return len(self.dataset)

    @property
    def description(self):
        return "{nb} submissions received on {date}".format(
            nb=self.nb_submissions,
            date=self.started_on.strftime('%d-%m-%Y'))
