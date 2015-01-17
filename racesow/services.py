# methods for performing business logic; reduces complexity of views

import platform
import re
from mgxrace import settings
from racesow.models import Race
from racesow.serializers import raceSerializer
from racesow.utils import average, floats_differ

if platform.system() == 'Linux':
    from time import time as time
elif platform.system() == 'Windows':
    from time import clock as time
else:
    raise ImportError("Expecting linux or windows")

MIN_REC_POINTS = 2
MAX_REC_POINTS = 100
SECOND_PLACE_PERC = 0.9  # 90% of 1st place
SKIP_BUMPTIME_OFFSET = 20  # number of completed races required for

# define playtime bumps for maps with fewer entries
BUMPTIME_LOW = 600000  # 10 minutes in millis
BUMPTIME_MEDIUM = 1800000  # 30 minutes in millis
BUMPTIME_HIGH = 3600000  # 60 minutes in millis

BUMP_POINTS = {
    BUMPTIME_LOW: 2,
    BUMPTIME_MEDIUM: 5,
    BUMPTIME_HIGH: 10,
}

_playerre = re.compile(r'player($|\(\d*\))', flags=re.IGNORECASE)


def map_get_rec_value(num_completed_races, races, best_race):
    """Compute the number of points to award the 1st player. It considers the amount of playtime other players spent on
     the map, the general idea being: more playtime && more players --> more points for 1st place.

    :param num_completed_races: number of Race objects with a time
    :param races: array of Race objects, sorted by playtime (desc)
    :return: points to award to 1st place (value between MIN_REC_POINTS and MAX_REC_POINTS)
    """

    # if num_completed_races >= SKIP_BUMPTIME_OFFSET:
    #     # enough top entries, rec is worth the maximum number of points
    #     return MAX_REC_POINTS

    # determine rec points from playtimes
    rec_points = MIN_REC_POINTS

    # bump rec_points for every player with significant playtime on this map
    for race in races:
        if race.pk == best_race.pk:
            # The fastest player cannot increase his own score by playing longer. On the contrary: the more he
            # plays, the more he bumps the score in case another player takes the rec. As points are always
            # calculated from scratch, the rec will be worth less when he re-recs because his own playtime is once
            # again excluded.
            continue

        if race.playtime > BUMPTIME_HIGH:
            rec_points += BUMP_POINTS[BUMPTIME_HIGH]
        elif race.playtime > BUMPTIME_MEDIUM:
            rec_points += BUMP_POINTS[BUMPTIME_MEDIUM]
        elif race.playtime > BUMPTIME_LOW:
            rec_points += BUMP_POINTS[BUMPTIME_LOW]
        else:
            # no significant Race objects left, break loop
            break

    # check whether we are not exceeding maximum value
    return min(rec_points, MAX_REC_POINTS)


def map_evaluate_points(mid, rec_points=None, completed_races=None, all_races=None):
    """Evaluates points awarded to races for map 'mid'.

    rec_points, completed_races and all_races can be passed as parameters to save time"""

    t_start = time()
    num_completed_races = 0
    try:
        # get Race objects with times (sorted by racetime ascendingly)
        if not completed_races:
            completed_races = Race.objects.filter(map__id=mid, time__isnull=False).order_by('time')
        num_completed_races = len(completed_races)

        if num_completed_races == 0:
            # no races to award points
            return

        # get all Race objects (sorted by playtime descendingly)
        if not all_races:
            all_races = Race.objects.filter(map__id=mid).order_by('-playtime')

        # determine points for first place
        best_race = completed_races[0]
        if not rec_points:
            rec_points = map_get_rec_value(num_completed_races, all_races, best_race)

        # award points to the fastest player
        best_race.set_points(rec_points)
        best_race.save()

        if num_completed_races == 1:
            # no further races to award points
            return

        top20avg = average([race.time for race in completed_races[:20]])  # average of top 20 racetimes

        # cap 2nd place by predefined percentage, with a minimum points difference of 2
        second_place_cap = min(rec_points - 2, rec_points * SECOND_PLACE_PERC)
        x = second_place_cap * (7 / 9)
        first_time = best_race.time

        # compute points for 2nd place (capped to a certain percentage of 1st place)
        second_place_points = min(second_place_cap, second_place_cap -
                                  (x * ((completed_races[1].time - first_time) / (top20avg * 0.8))))

        # award the points
        completed_races[1].set_points(second_place_points)
        completed_races[1].save()

        if num_completed_races == 2:
            # no further races to award points
            return

        # award points for 3rd, 4th... place by differentiating their times with first place, with a minimum of 2
        # points to the previous time
        points_above = second_place_points
        for race in completed_races[2:]:
            calculated_points = max(0, min(points_above - 2, second_place_cap -
                                           (x * ((race.time - first_time) / (top20avg * 0.8)))))
            race.set_points(calculated_points)
            race.save()
            points_above = calculated_points
    finally:
        calc_time = time() - t_start
        if settings.DEBUG:
            print "map_evaluate_points({}, rec_points={}) completed in {:.3f} seconds (num_completed_races {})".format(
                mid, rec_points, calc_time, num_completed_races)


def player_process_playtime(player, mid):
    """Compare rec_points after a player's updated playtime on map 'mid' has been stored. If rec_points is changed,
    the map points need to be updated, otherwise we can save the effort."""

    # get Race objects with times (sorted by racetime ascendingly)
    completed_races = Race.objects.filter(map__id=mid, time__isnull=False).order_by('time')
    if not completed_races:
        # no times on this map yet
        return
    best_race = completed_races[0]
    cur_rec_points = best_race.get_points()

    if best_race.player.pk == player.pk:
        # the fastest player cannot increase his own score by playing longer
        if settings.DEBUG:
            print "player_process_playtime({}, {}) fastest player does not trigger map_evaluate_points".format(
                player, mid)
        return

    # get all Race objects (sorted by playtime descendingly)
    all_races = Race.objects.filter(map__id=mid).order_by('-playtime')

    # determine points for first place
    new_rec_points = map_get_rec_value(len(completed_races), all_races, best_race)

    if floats_differ(cur_rec_points, new_rec_points):
        # rec_points is changed by the added playtime, changes, re-evaluate map points.
        if settings.DEBUG:
            print "player_process_playtime({}, {}) cur_rec_points %.3f, new_rec_points %.3f --> re-evaluate map points"\
                .format(player, mid, cur_rec_points, new_rec_points)
        map_evaluate_points(mid, rec_points=new_rec_points, completed_races=completed_races, all_races=all_races)
        return True
    if settings.DEBUG:
        print "player_process_playtime({}, {}) cur_rec_points %.3f, new_rec_points %.3f --> do nothing"\
            .format(player, mid, cur_rec_points, new_rec_points)
    return False


def get_record(flt):
    """
    Get the maps serialized record race

    Args:
        flt - A kwarg dict to filter race objects by

    Returns:
        The serialized race dictionary or None if no race exists
    """
    try:
        record = Race.objects.filter(time__isnull=False, **flt).order_by('time')[0]
        return raceSerializer(record)
    except:
        return None


def is_default_username(username):
    # returns True if username is like 'player', 'player(1)' etc.
    return _playerre.match(username)