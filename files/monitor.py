#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from urlparse import urlparse, parse_qs
except ImportError:
    # Python 3
    unicode = str
    from urllib.parse import urlparse, parse_qs

from tornado import web
from prometheus_client import core, Histogram, Counter, Gauge

import log

_log = log.get_log(__name__)


class _Handler(web.RequestHandler):
    '''
    copy from the prometheus_client.exposition.py
    https://github.com/prometheus/client_python/blob/master/prometheus_client/exposition.py
    '''
    def __generate_latest(self, registry=core.REGISTRY):
        '''Returns the metrics from the registry
        in latest text format as a string.
        '''
        output = []
        for metric in registry.collect():
            output.append('# HELP {0} {1}'.format(
                metric.name,
                metric.documentation
                .replace('\\', r'\\')
                .replace('\n', r'\n')))
            output.append('\n# TYPE {0} {1}\n'.format(metric.name,
                                                      metric.type))
            for name, labels, value in metric.samples:
                labelstr = '{{{0}}}'.format(','.join(
                        ['{0}="{1}"'.format(k, v.replace('\\', r'\\')
                                            .replace('\n', r'\n')
                                            .replace('"', r'\"'))
                         for k, v
                         in sorted(labels.items())])) if labels else ''

                output.append('%s%s %s\n' % (name,
                                             labelstr,
                                             core._floatToGoString(value)))
        return ''.join(output).encode('utf-8')

    def get(self):
        self.set_header('Content-Type',
                        str('text/plain; version=0.0.4; charset=utf-8'))
        registry = self.get_query_argument('name[]', None) or core.REGISTRY
        self.write(self.__generate_latest(registry))


_http_request_total = Counter('http_request_total',
                              'http request total count',
                              ['handler', 'method'])

_http_request_failure = Counter('http_request_failure_total',
                              'http request total failure',
                              ['handler'])


def http_request_total(handler, method):
    _http_request_total.labels(handler, method).inc()


def http_request_failure_total(handler):
    _http_request_failure_total.labels(handler).inc()

_http_request_duration_seconds = Histogram('http_request_duration_seconds',
                                           'http response time',
                                           ['handler', 'method', 'code'],
                                           buckets=[.5, 1, 2, 4, 8, 12, 16])


def http_request_duration(handler, method, status_code, secs):
    _http_request_duration_seconds.labels(handler,
                                          method,
                                          status_code).observe(secs)


_operation_duration_seconds = Histogram('operation_duration_seconds',
                                        'the cost time of some operation',
                                        ['operation'],
                                        buckets=[.5, 1, 2, 4, 8, 12, 16])


def operation_duration(operation, secs):
    _operation_duration_seconds.labels(operation).observe(secs)


def remote_request_duration(handler, secs):
    operation_duration(':'.join([handler, 'remote']), secs)


_what_total = Counter('what_total',
                      'the counter of something',
                      ['what'])


def inc_what_total(what, inc=1):
    _what_total.labels(what).inc(inc)


def inc_image_download_error(handler, inc=1):
    inc_what_total(':'.join([handler, 'download_image_error']), inc)


_what_size = Gauge('what_size',
                   'the size of something',
                   ['what'])


def what_size(what, size):
    _what_size.labels(what).set(size)


def inc_eval_queue_size(name, inc=1):
    _what_size.labels(name).inc(inc)


def init(app):
    app.add_handlers('.*$', [(r'/metrics', _Handler)])
