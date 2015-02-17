import logging

import celery
from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View

from racesow.models import Map, Race, Player
from racesowold.models import Map as Mapold, PlayerMap, Player as Playerold


__author__ = 'Mark'

PAGE_LIMIT = 20


def get_page(objects, page):
    # limit results per page, create paginator object
    paginator = Paginator(objects, PAGE_LIMIT)
    try:
        objects_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        objects_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        objects_page = paginator.page(paginator.num_pages)
    return objects_page


class Index(View):
    def get(self, request):
        context = {
            'races': Race.objects.filter(time__isnull=False).order_by('-created').select_related('map', 'player')[:20]}
        return render(request, 'racesow/home.html', context)


class MapList(View):
    def maplist_validate_order(self, order, version):
        if version == 'new':
            # compare order with valid table header orderings
            # Name  Races-  Playtime  DL  Tags
            if order not in ['name', 'races', 'playtime',
                             '-name', '-races', '-playtime']:
                order = 'name'
        elif version == 'old':
            # compare order with valid table header orderings
            #  Name  Weapons  Races-  Playtime  DL  Long name
            if order not in ['name', 'weapons', 'races', 'playtime', 'longname',
                             '-name', '-weapons', '-races', '-playtime', '-longname']:
                order = 'name'
        else:
            raise Http404
        return order

    def get(self, request, version, **kwargs):
        context = {'version': version}
        db_filter = {}
        maplist_url = 'rs:mln3' if version == 'new' else 'rs:mlo3'  # url to put in table <a> href
        page = kwargs.get('page', 1)
        order = self.maplist_validate_order(kwargs.get('order', ''), version)

        try:
            # update filter with search query, if any
            q = kwargs['q']
            if not q:  # redirect to different url if query empty
                return redirect(maplist_url, order=order, page=page)
            db_filter.update({'name__icontains': q})
        except:
            try:
                q = request.GET['q']
                # redirect to different url if a GET request was passed
                return redirect(maplist_url, order=order,  page=page, q=q.replace(' ', ''))
            except:
                q = ''

        if settings.DEBUG:
            print u"MapList.get(version={}, order={}, page={}, q={})".format(version, order, page, q)

        if version == 'new':
            db_filter.update({'enabled': True})
            db_order_l = [order]
            if order.endswith('races'):
                # append name as 2nd order for columns with equal rows
                db_order_l.append('name')

            # prefetch_related because tags is a many-to-many relationship
            maps_list = Map.objects.filter(**db_filter).order_by(*db_order_l).prefetch_related('tags')

            # specify the url to put in <form> href
            context.update({'form_url': 'rs:mln'})
        else:
            db_filter.update({'status': 'enabled'})
            db_order_l = [order]
            if order.endswith('weapons') or order.endswith('races'):
                db_order_l.append('name')  # append name as 2nd order for alphabetic ordering

            maps_list = Mapold.objects.filter(**db_filter).order_by(*db_order_l)

            # specify the url to put in <form> href
            context.update({'form_url': 'rs:mlo'})

        context.update({'maps': get_page(maps_list, page), 'maplist': maplist_url, 'order': order, 'query': q})
        return render(request, 'racesow/maps.html', context)


class MapDetails(View):
    def mapdetails_validate_order(self, order, version):
        if version == 'new':
            # compare order with valid table header orderings
            if order not in ['points', 'time', 'player', 'playtime', 'date',
                             '-points', '-time', '-player', '-playtime', '-date']:
                order = 'time'  # default
        elif version == 'old':
            # compare order with valid table header orderings
            if order not in ['points', 'time', 'player', 'onlinetime', 'date',
                             '-points', '-time', '-player', '-onlinetime', '-date']:
                order = 'time'  # default
        else:
            raise Http404
        return order

    def get(self, request, version, **kwargs):
        context = {'version': version}
        mapdetails_url = 'rs:mdn2' if version == 'new' else 'rs:mdo2'  # url to put in table <a> href
        page = kwargs.get('page', 1)
        map_id = kwargs['mapid']
        order = self.mapdetails_validate_order(kwargs.get('order', ''), version)

        if settings.DEBUG:
            print u"PlayerDetails.get(version={}, order={}, page={})".format(version, order, page)

        # retrieve version-specific map details
        if version == 'new':
            # get map object
            try:
                map_ = Map.objects.get(pk=map_id)
            except Map.DoesNotExist:
                return render(request, 'racesow/map.html', context)

            # try to get map object for other version based on name
            try:
                map_other = Mapold.objects.get(name=map_.name)
                context.update({'map_other': map_other, 'mapdetails_other': 'rs:mdo', 'version_other': 'old'})
            except Mapold.DoesNotExist:
                pass

            # translate table column to a database column
            db_order = order
            if db_order.endswith('player'):
                db_order = order.replace('player', 'player__simplified')
            elif db_order.endswith('date'):
                db_order = order.replace('date', 'created')

            races_list = Race.objects.filter(map__id=map_.id).exclude(time__isnull=True).order_by(db_order).select_related('player')
        else:
            # get map object
            try:
                map_ = Mapold.objects.get(pk=map_id)
            except Mapold.DoesNotExist:
                return render(request, 'racesow/map.html', context)

            # try to get map object for other version based on name
            try:
                map_other = Map.objects.get(name=map_.name)
                context.update({'map_other': map_other, 'mapdetails_other': 'rs:mdn', 'version_other': 'new'})
            except Map.DoesNotExist:
                pass

            # translate table column to a database column
            db_order = order
            if db_order.endswith('player'):
                db_order = order.replace('player', 'player__simplified')
            elif db_order.endswith('onlinetime'):
                db_order = order.replace('onlinetime', 'playtime')
            elif db_order.endswith('date'):
                db_order = order.replace('date', 'created')

            races_list = PlayerMap.objects.filter(map__id=map_.id)\
                .exclude(time__isnull=True).order_by(db_order).select_related('player')

        context.update({'map': map_, 'mapdetails': mapdetails_url, 'races': get_page(races_list, page), 'order': order})
        return render(request, 'racesow/map.html', context)


class PlayerList(View):
    def playerlist_validate_order(self, order, version):
        if version == 'new':
            # compare order with valid table header orderings
            if order not in ['name', 'points', 'skill', 'maps', 'races', 'playtime',
                             '-name', '-points', '-skill', '-maps', '-races', '-playtime']:
                order = '-races'  # default
        elif version == 'old':
            # compare order with valid table header orderings
            if order not in ['name', 'points', 'skill', 'maps', 'races', 'playtime',
                             '-name', '-points', '-skill', '-maps', '-races', '-playtime']:
                order = '-points'  # default
        else:
            raise Http404
        return order

    def get(self, request, version, **kwargs):
        context = {'version': version}
        playerlist_url = 'rs:pln3' if version == 'new' else 'rs:plo3'  # url to put in table <a> href
        db_filter = {}
        page = kwargs.get('page', 1)
        order = self.playerlist_validate_order(kwargs.get('order', ''), version)

        try:
            # update filter with search query, if any
            q = kwargs['q']
            if not q:  # redirect to different url if query empty
                return redirect(playerlist_url, order=order, page=page)
            db_filter.update({'simplified__icontains': q})
        except:
            try:
                q = request.GET['q']
                # redirect to different url if a GET request was passed
                return redirect(playerlist_url, order=order,  page=page, q=q.replace(' ', ''))
            except:
                q = ''

        if settings.DEBUG:
            print u"PlayerList.get(version={}, order={}, page={}, q={})".format(version, order, page, q)

        if version == 'new':
            db_order_l = [order]
            if order.endswith('name'):
                # don't order by 'name' because it contains colorcodes
                db_order_l[0] = order.replace('name', 'simplified')
            elif order.endswith('races') \
                    or order.endswith('points') \
                    or order.endswith('skill'):
                # append simplified as 2nd order for columns with equal rows
                db_order_l.append('simplified')

            # get players matching filter and ordering criteria
            player_list = Player.objects.filter(**db_filter).order_by(*db_order_l)\
                .extra(select={'skill': 'IF(maps_finished >= 5, points/maps_finished/1000, 0)'})

            # specify the url to put in <form> href
            context.update({'form_url': 'rs:pln'})
        else:
            db_order_l = [order]
            if order.endswith('name'):
                # don't order by 'name' because it contains colorcodes
                db_order_l[0] = order.replace('name', 'simplified')
            elif order.endswith('points') \
                    or order.endswith('skill') \
                    or order.endswith('maps') \
                    or order.endswith('races'):
                # append simplified as 2nd order for columns with equal rows
                db_order_l.append('simplified')

            # define skill column (original query: IF(`maps`>=30,`points`/`maps`,0) AS `skill`)
            player_list = Playerold.objects.filter(**db_filter).order_by(*db_order_l)\
                .extra(select={'skill': 'IF(maps >= 30, points/maps, 0)'})

            # specify the url to put in <form> href
            context.update({'form_url': 'rs:plo'})

        context.update(
            {'players': get_page(player_list, page), 'playerlist': playerlist_url, 'order': order, 'query': q})
        return render(request, 'racesow/players.html', context)


class PlayerDetails(View):
    def playerdetails_validate_order(self, order, version):
        if version == 'new':
            # compare order with valid table header orderings
            # Name  Time  Playtime Date
            if order not in ['name', 'points', 'time', 'playtime', 'date',
                             '-name', '-points', '-time', '-playtime', '-date']:
                order = '-points'  # default
        elif version == 'old':
            # compare order with valid table header orderings
            # Name  Points-  Time  Playtime Date
            if order not in ['name', 'points', 'time', 'onlinetime', 'date',
                             '-name', '-points', '-time', '-onlinetime', '-date']:
                order = '-points'  # default
        else:
            raise Http404
        return order

    def get(self, request, version, **kwargs):
        context = {'version': version}
        playerdetails_url = 'rs:pdn3' if version == 'new' else 'rs:pdo3'  # url to put in table <a> href
        db_filter = {}
        page = kwargs.get('page', 1)
        player_id = kwargs['playerid']
        order = self.playerdetails_validate_order(kwargs.get('order', ''), version)

        try:
            # update filter with search query, if any
            q = kwargs['q']
            if not q:  # redirect to different url if query empty
                return redirect(playerdetails_url, playerid=player_id, order=order, page=page)
            db_filter.update({'map__name__icontains': q})
        except:
            try:
                q = request.GET['q']
                # redirect to different url if a GET request was passed
                return redirect(playerdetails_url, playerid=player_id, order=order,  page=page, q=q.replace(' ', ''))
            except:
                q = ''

        if settings.DEBUG:
            print u"PlayerDetails.get(version={}, order={}, page={}, q={})".format(version, order, page, q)

        # retrieve player-specific details
        if version == 'new':
            # get player object
            try:
                player = Player.objects.get(pk=player_id)
            except Player.DoesNotExist:
                return render(request, 'racesow/player.html', context)
            db_filter.update({'player__id': player_id, 'time__isnull': False})

            # try to get player object(s) for other version based on simplified name.
            # Sort by points and take the first player when there is more than 1 result.
            player_other_list = Playerold.objects.filter(simplified=player.simplified).order_by('-points')
            if player_other_list:
                context.update({'player_other': player_other_list[0], 'playerdetails_other': 'rs:pdo', 'version_other': 'old'})

            # translate table column to a database column
            db_order_l = [order]
            if order.endswith('name'):
                db_order_l[0] = order.replace('name', 'map__name')
            elif order.endswith('date'):
                db_order_l[0] = order.replace('date', 'created')
            elif order.endswith('points'):
                # append time as 2nd order for columns with equal rows
                db_order_l.append('time')

            pmaps_list = Race.objects.filter(**db_filter).order_by(*db_order_l).select_related('map', 'player')

            player.skill = player.get_points() / player.maps_finished if player.maps_finished else 0
            player.pmaps = len(pmaps_list)

            context.update({'medals': {
                'gold': len(Race.objects.filter(player=player, rank=1)),
                'silver': len(Race.objects.filter(player=player, rank=2)),
                'bronze': len(Race.objects.filter(player=player, rank=3))}
            })

            # specify the url to put in <form> href
            context.update({'form_url': 'rs:pdn'})
        else:
            # get player object
            try:
                player = Playerold.objects.get(pk=player_id)
            except Playerold.DoesNotExist:
                return render(request, 'racesow/player.html', context)
            db_filter.update({'player__id': player_id, 'time__isnull': False})

            # try to get player object(s) for other version based on simplified name.
            # Sort by points and take the first player when there is more than 1 result.
            player_other_list = Player.objects.filter(simplified=player.simplified).order_by('-points')
            if player_other_list:
                context.update({'player_other': player_other_list[0], 'playerdetails_other': 'rs:pdn', 'version_other': 'new'})

            # translate table column to a database column
            db_order_l = [order]
            if order.endswith('name'):
                db_order_l[0] = order.replace('name', 'map__name')
            elif order.endswith('onlinetime'):
                db_order_l[0] = order.replace('onlinetime', 'playtime')
            elif order.endswith('date'):
                db_order_l[0] = order.replace('date', 'created')
            elif order.endswith('points'):
                # append time as 2nd order for columns with equal rows
                db_order_l.append('time')

            pmaps_list = PlayerMap.objects.filter(**db_filter).order_by(*db_order_l).select_related('map', 'player')

            context.update({'medals': {
                'gold': len(PlayerMap.objects.filter(player__id=player.id, points=40)),
                'silver': len(PlayerMap.objects.filter(player__id=player.id, points=34)),
                'bronze': len(PlayerMap.objects.filter(player__id=player.id, points=31))}
            })

            player.skill = float(player.points) / player.maps
            player.pmaps = len(pmaps_list)

            # specify the url to put in <form> href
            context.update({'form_url': 'rs:pdo'})

        context.update({'player': player, 'pmaps': get_page(pmaps_list, page), 'playerdetails': playerdetails_url,
                        'order': order, 'query': q})
        return render(request, 'racesow/player.html', context)