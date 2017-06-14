#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author : zenk
# 2016-11-21 10:29
import logging
import logging.config


def init(config):
    logging.config.dictConfig(config)


def get_log(name=''):
    return logging.getLogger(name or '')


PROD = dict(
    version=1,
    formatters={
        'default': {
            'format': '%(asctime)s [%(threadName)s] '
            '%(levelname)s [%(name)s] %(message)s'
        }
    },
    filters={
    },
    handlers={
        'file': {
            'level': 'DEBUG',
            'formatter': 'default',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'midnight',
            'filename': 'app.log',
            'encoding': 'utf-8'
        },
        'console': {
            'level': 'DEBUG',
            'formatter': 'default',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout'
        }
    },
    root={
        'level': 'DEBUG',
        'handlers': ['console']
    },
    loggers={
        'tornado': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False
        },
        'app': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False
        },
        'tests': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False
        }
    }
)

TEST = dict(
    version=1,
    formatters={
        'default': {
            'format': '%(asctime)s [%(threadName)s] '
            '%(levelname)s [%(name)s] %(message)s'
        }
    },
    filters={
    },
    handlers={
        'file': {
            'level': 'DEBUG',
            'formatter': 'default',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'midnight',
            'filename': 'app.log',
            'encoding': 'utf-8'
        },
        'console': {
            'level': 'DEBUG',
            'formatter': 'default',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout'
        }
    },
    root={
        'level': 'DEBUG',
        'handlers': ['file', 'console']
    },
    loggers={
        'tornado': {
            'level': 'DEBUG',
            'handlers': ['file', 'console'],
            'propagate': False
        },
        'app': {
            'level': 'DEBUG',
            'handlers': ['file', 'console'],
            'propagate': False
        },
        'tests': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False
        }
    }
)
