from __future__ import absolute_import

import time
import datetime

from celery import shared_task
from celery.utils.log import get_task_logger

from .models import Map, Player, Race
from racesow import services


logger = get_task_logger(__name__)


@shared_task
def force_recompute_all():
    logger.info("force_recompute_all starting")

    # reset all player point/maps_finished totals
    for player in Player.objects.all():
        player.maps_finished = 0
        player.points = 0
        player.save()

    # re-evaluate points for all maps
    for map_ in Map.objects.all():
        # awards points to finished races on this map.
        services.map_evaluate_points(map_.id, reset=True)
        # reset=True indicates that all Player.points/Player.maps_finished columns have been set to 0 and that the
        # current Race.points values should be discarded. The method recomputes Race.points for all players, adds this
        # to Player.points and increments Player.finished_maps

        map_.compute_points = False
        map_.last_computation = datetime.datetime.now()
        map_.save()

    # Check for races made during this task.
    # This is necessary to prevent races from staying at -1 points for possibly long periods of time
    while True:
        new_races = Race.objects.filter(time__isnull=False, points=-1000)
        new_races.query.group_by = ['map_id']

        if not new_races:
            logger.info("force_recompute_all done")
            return
        # else: new races were registered during this task and map_.compute_points was overwritten

        logger.info("{} maps updated during task".format(len(new_races)))

        for race in new_races:
            # set recompute bit for each map..
            race.map.compute_points = True

        # update these maps using the normal task
        recompute_updated_maps()


# scheduled to run every 5 minutes
@shared_task
def recompute_updated_maps():
    maps_updated = 0
    for map_ in Map.objects.filter(compute_points=True):
        services.map_evaluate_points(map_.id, reset=False)
        # Recomputes Race points for this map and update Player totals.
        # For every player that didn't have points yet for their race:
        # race.points = computed_points
        #       player.points += Race.points
        #       player.finished_maps += 1
        # else if the player's recomputed points are different from the current value (by a 0.01 margin)
        #       old_points = race.points
        #       player.points += (computed_points - old_points)
        #       race.points = computed_points

        map_.compute_points = False
        map_.last_computation = datetime.datetime.now()
        map_.save()
        maps_updated += 1
    return maps_updated