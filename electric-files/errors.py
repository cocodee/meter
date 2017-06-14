#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author : zenk
# 2016-11-18 11:43
from collections import namedtuple

Error = namedtuple('Error', ['status_code', 'detail'])
Detail = namedtuple('Detail', ['code', 'message'])


def create_download_error(name, error='download failed'):
    # id for ``post_eval``
    return dict(code=400, message=error, name=name, id=name)


def create_success(display,confidence,typ):
    return {
        'code': 200,
        'message': 'Success',
        'display':display,
        'confidence':confidence,
        'type':typ
    }


def create_error(code, name, message):
    return dict(code=code, message=message, name=name)


def create_server_error(message, code=90):
    return Error(400, Detail(code, message))


def create_unavailable_error(message, code):
    return Error(503, Detail(code, message))


NO_RESOURCE = Error(400, Detail(41, 'no resource'))
DOWNLOAD_ERROR = Error(400, Detail(40, 'download failed'))

SERVER_ERROR_PRE_EVAL = create_server_error('pre eval error', 50)
SERVER_ERROR_EVAL = create_server_error('eval error', 60)
SERVER_ERROR_POST_EVAL = create_server_error('post eval error', 70)
SERVER_ERROR_LACK_DISK_SPACE = create_unavailable_error('lack disk space',
                                                        code=81)
