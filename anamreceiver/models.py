#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import os
import json
import logging

from django.db import models
from django.conf import settings
from django.utils import timezone
from jsonfield.fields import JSONField

logger = logging.getLogger(__name__)


class Collect(models.Model):

    started_on = models.DateTimeField(auto_now_add=True)
    dataset = JSONField(default={}, blank=True)
    targets = JSONField(default={}, blank=True)
    imported_on = models.DateTimeField(null=True, blank=True)
    images_copied_on = models.DateTimeField(null=True, blank=True)
    images_nb_total = models.PositiveIntegerField(null=True, blank=True)
    images_nb_error = models.PositiveIntegerField(null=True, blank=True)
    archived = models.BooleanField(default=False)

    nb_submissions = models.PositiveIntegerField(null=True, blank=True)
    cercle = models.CharField(max_length=200, null=True, blank=True)
    commune = models.CharField(max_length=200, null=True, blank=True)
    ona_form_id = models.CharField(max_length=200, null=True, blank=True)
    ona_scan_form_id = models.CharField(max_length=200, null=True, blank=True)

    @classmethod
    def create(cls, dataset):
        collect = cls.objects.create()
        with open(collect.dataset_path, "w") as fh:
            json.dump(dataset, fh)
        collect.save_metadata(dataset)

    def save_metadata(self, dataset):
        self.nb_submissions = len(dataset.get("targets", []))
        self.cercle = dataset.get("cercle")
        self.commune = dataset.get("commune")
        self.ona_form_id = dataset.get("ona_form_id")
        self.ona_scan_form_id = dataset.get("ona_scan_form_id")
        self.dataset = {}
        self.targets = {}
        self.save()

    @property
    def dataset_path(self):
        return os.path.join(settings.FILES, "{}_dataset.json".format(self.id))

    @property
    def targets_path(self):
        return os.path.join(settings.FILES, "{}_targets.json".format(self.id))

    @property
    def dataset_file(self):
        with open(self.dataset_path, "r") as fh:
            return json.load(fh)

    @property
    def targets_file(self):
        with open(self.targets_path, "r") as fh:
            return json.load(fh)

    @property
    def description(self):
        return "{nb} submissions received on {date}".format(
            nb=self.nb_submissions,
            date=self.started_on.strftime('%d-%m-%Y'))

    @property
    def imported(self):
        return self.imported_on is not None

    @property
    def images_copied(self):
        return self.images_copied_on is not None

    @property
    def images_copied_all_successful(self):
        return self.images_copied and self.images_nb_error == 0

    @property
    def nb_indigents(self):
        # now equal to submissions as every target an indigent
        # return len(self.get_indigents())
        return self.nb_submissions

    # def get_indigents(self):
    #     return [target
    #             for target in self.dataset_file.get('targets', [])
    #             if True]  # target.get('certificat-indigence')]

    @property
    def can_be_imported(self):
        return self.nb_indigents > 0 and not self.imported

    @property
    def can_be_copied(self):
        return self.nb_indigents > 0 and not self.images_copied \
            and self.imported

    def to_dict(self):
        return {
            'id': self.id,
            'archived': self.archived,
            'nb_submissions': self.nb_submissions,
            'started_on': self.started_on.isoformat(),
            'imported': self.imported,
            'images_copied': self.images_copied,
            'imported_on': self.imported_on.isoformat()
            if self.imported_on else None,
            'images_copied_on': self.images_copied_on.isoformat()
            if self.images_copied_on else None,
            'can_be_imported': self.can_be_imported,
            'can_be_copied': self.imported,
            'images_nb_total': self.images_nb_total,
            'images_nb_error': self.images_nb_error,

            'cercle': self.cercle,
            'commune': self.commune,

            'ona_form_id': self.ona_form_id,
            'ona_scan_form_id': self.ona_scan_form_id,
        }

    def full_dict(self):
        d = self.to_dict()
        d.update({'dataset': self.dataset_file})
        d.update({'targets': self.targets_file})
        return d

    def mark_imported(self, targets):
        # save targets to file
        with open(self.targets_file, "w") as fh:
            json.dump(targets, fh, indent=4)
        # self.targets = targets
        self.imported_on = timezone.now()
        self.save()

    def mark_images_copied(self, images_nb_total, images_nb_error):
        self.images_copied_on = timezone.now()
        self.images_nb_total = images_nb_total
        self.images_nb_error = images_nb_error
        self.save()

    def mark_archived(self):
        self.archived = True
        self.save()

    def unmark_archived(self):
        self.archived = False
        self.save()
