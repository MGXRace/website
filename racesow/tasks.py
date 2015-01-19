from __future__ import absolute_import
import logging

from celery import shared_task
import time
from celery.utils.log import get_logger
from .models import Map


@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y

@shared_task
def xsum(numbers):
    l_ = logging.getLogger('django')
    l_.info("XSUM TEST")
    time.sleep(5)
    l_.info("XSUM TEST KLAAR ")
    return sum(numbers)

@shared_task
def update_oneliner(mapname, new_oneliner):
    l_ = logging.getLogger('django')
    l_.info("update_oneliner {} {} started, will complete in 10 seconds".format(mapname, new_oneliner))
    time.sleep(10)
    try:
        map_ = Map.objects.get(name=mapname)
        old = map_.oneliner
        map_.oneliner = new_oneliner
        map_.save()
        l_.info("update_oneliner {} updated oneliner from [{}] to [{}]!".format(mapname, old, new_oneliner))
    except Map.DoesNotExist:
        l_.info("update_oneliner {} {} failed!".format(mapname, new_oneliner))