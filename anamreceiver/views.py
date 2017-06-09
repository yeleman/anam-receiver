#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import logging
import json

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse

from anam.models import Collect

logger = logging.getLogger(__name__)


def home(request):
    context = {
        'collects': Collect.objects.all(),
    }
    return render(request, 'home.html', context)


@require_POST
@csrf_exempt
def upload(request):
    try:
        dataset = json.loads(request.body.decode('UTF-8'))
        collect = Collect.objects.create(dataset=dataset)
    except Exception as exp:
        return JsonResponse({'status': 'failed', 'message': str(exp)})
    else:
        return JsonResponse({'status': 'success',
                             'message': collect.description})

