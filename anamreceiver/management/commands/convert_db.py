#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import os
import json
import logging

from django.conf import settings
from django.db import connection, transaction
from django.core.management.base import BaseCommand

from anamreceiver.models import Collect

logger = logging.getLogger(__name__)


def convert_collect(collect):
    with open(collect.dataset_path, "w") as fh:
        json.dump(collect.dataset, fh, indent=4)

    with open(collect.targets_path, "w") as fh:
        json.dump(collect.targets, fh, indent=4)

    dataset = collect.dataset_file
    collect.save_metadata(dataset)


class Command(BaseCommand):
    help = "Convert all existing Collect to files-hosted"

    def handle(self, *args, **kwargs):
        if not os.path.exists(settings.FILES):
            os.mkdir(settings.FILES)

        for collect in Collect.objects.all():
            print("converting", collect)
            convert_collect(collect)

        with connection.cursor() as cursor:
            print("vacuming…")
            cursor.execute("vacuum;")
            transaction.commit()
