#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import json
import lzma
import logging
from functools import wraps

from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseForbidden

from anamreceiver.models import Collect

logger = logging.getLogger(__name__)


def req_token(view_func, registry):
    ''' generic decorator to check Authorization header for a token '''
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated():
            return view_func(request, *args, **kwargs)
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if 'token' in auth_header.lower():
            token = auth_header.split(" ", 1)[-1]
            if token.upper() in registry:
                return view_func(request, *args, **kwargs)
        return HttpResponseForbidden()
    return _wrapped_view


def admin_token(view_func):
    ''' authentication decorator for admin-only views '''
    return req_token(view_func, settings.ADMIN_TOKENS)


def upload_token(view_func):
    ''' authentication decorator for upload-only views '''
    return req_token(view_func, settings.UPLOAD_TOKENS)


def any_token(view_func):
    ''' authentication decorator '''
    return req_token(view_func, settings.UPLOAD_TOKENS + settings.ADMIN_TOKENS)


def home(request):
    ''' basic public list of received collects '''
    context = {
        'collects': Collect.objects.order_by('-id'),
    }
    return render(request, 'home.html', context)


@admin_token
def check(request):
    ''' check whether the service is up and running

        used by anam-desktop to check url+token '''
    return JsonResponse({'status': 'success', 'message': "OK"})


@admin_token
def all_collects(request):
    ''' complete list of all collects (only metadata for each) '''
    return JsonResponse({
        'status': 'success',
        'collects': [collect.to_dict()
                     for collect in Collect.objects.order_by('-id')]})


@admin_token
def single_collect(request, collect_id):
    ''' details of a single collect: metadata + dataset + targets '''
    collect = Collect.objects.get(id=collect_id)
    return JsonResponse({
        'status': 'success',
        'collect': collect.full_dict()})


@any_token
@require_POST
@csrf_exempt
def api_upload(request):
    ''' JSON upload endpoint for sending a single collect data '''

    if 'xzfile' in request.FILES:
        try:
            body = lzma.decompress(request.FILES['xzfile'].read())
        except Exception as exp:
            return JsonResponse({'status': 'failed',
                                 'message': "Failed to uncompress data: {}"
                                 .format(exp)})
    else:
        body = request.body

    try:
        dataset = json.loads(body.decode('UTF-8'))
        collect = Collect.objects.create(dataset=dataset)
    except Exception as exp:
        return JsonResponse({'status': 'failed', 'message': str(exp)})
    else:
        return JsonResponse({'status': 'success',
                             'message': collect.description})


@admin_token
@require_POST
@csrf_exempt
def mark_imported(request, collect_id):
    ''' marks collect as imported now and store submitted targets matching '''
    collect = Collect.objects.get(id=collect_id)
    try:
        targets = json.loads(request.body.decode('UTF-8'))
        collect.mark_imported(targets)
    except Exception as exp:
        return JsonResponse({'status': 'failed', 'message': str(exp)})
    else:
        return JsonResponse({'status': 'success',
                             'message': collect.description})


@admin_token
@require_POST
@csrf_exempt
def mark_images_copied(request, collect_id):
    ''' marks collect as having its images copied and store errors status '''
    collect = Collect.objects.get(id=collect_id)
    try:
        payload = json.loads(request.body.decode('UTF-8'))
        collect.mark_images_copied(
            images_nb_total=payload['images_nb_total'],
            images_nb_error=payload['images_nb_error'])
    except Exception as exp:
        return JsonResponse({'status': 'failed', 'message': str(exp)})
    else:
        return JsonResponse({'status': 'success',
                             'message': collect.description})


@admin_token
@require_POST
@csrf_exempt
def archive(request, collect_id):
    ''' marks collect as archived '''
    collect = Collect.objects.get(id=collect_id)
    try:
        collect.mark_archived()
    except Exception as exp:
        return JsonResponse({'status': 'failed', 'message': str(exp)})
    else:
        return JsonResponse({'status': 'success',
                             'message': collect.description})


@admin_token
@require_POST
@csrf_exempt
def unarchive(request, collect_id):
    ''' marks collect as not archived '''
    collect = Collect.objects.get(id=collect_id)
    try:
        collect.unmark_archived()
    except Exception as exp:
        return JsonResponse({'status': 'failed', 'message': str(exp)})
    else:
        return JsonResponse({'status': 'success',
                             'message': collect.description})
