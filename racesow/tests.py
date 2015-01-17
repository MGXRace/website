"""
simple testcases, should be expanded for testing services.py

Usage (debian) from the /website directory:
    python manage.py test racesow
"""
import sys

from django.test import TestCase

from .models import (
    Map,
    Player,
    Race)
from racesow.utils import millis_to_str


class MapMethodTests(TestCase):
    def setUp(self):
        # settings.configure()
        pass

    def test_get_existing_map(self):
        insert_name = "MyTestMap"
        map_ = Map()
        map_.name = insert_name
        map_.save()

        try:
            Map.objects.get(name=insert_name)
        except:
            self.fail("Expected to find inserted map {}. Exception: {}".format(insert_name, sys.exc_type))

    def test_get_nonexisting_map(self):
        insert_name = "MyTestMap"
        select_name = "NotMyTestMap"
        map_ = Map()
        map_.name = insert_name
        map_.save()

        self.assertRaises(Map.DoesNotExist, Map.objects.get, name=select_name)

    def test_increment_map_playtime(self):
        insert_name = "MyTestMap"
        insert_playtime = 100
        add_playtime = 5
        map_ = Map()
        map_.name = insert_name
        map_.playtime = insert_playtime
        map_.save()

        map2 = Map.objects.get(name=insert_name)
        map2.playtime += add_playtime
        map2.save()

        map3 = Map.objects.get(name=insert_name)
        self.assertEqual(map3.playtime, insert_playtime + add_playtime)


class UtilsTests(TestCase):

    def setUp(self):
        pass

    def test_millis_to_str_1(self):
        str_ = "0.005"
        millis = 5
        self.assertEqual(millis_to_str(millis), str_)

    def test_millis_to_str_2(self):
        str_ = "9.986"
        millis = 9986
        self.assertEqual(millis_to_str(millis), str_)

    def test_millis_to_str_3(self):
        str_ = "29.999"
        millis = 29999
        self.assertEqual(millis_to_str(millis), str_)

    def test_millis_to_str_4(self):
        str_ = "59.999"
        millis = 59999
        self.assertEqual(millis_to_str(millis), str_)

    def test_millis_to_str_5(self):
        str_ = "1:00.000"
        millis = 60000
        self.assertEqual(millis_to_str(millis), str_)

    def test_millis_to_str_6(self):
        str_ = "1:00.001"
        millis = 60001
        self.assertEqual(millis_to_str(millis), str_)

    def test_millis_to_str_7(self):
        str_ = "1:24.172"
        millis = 84172
        self.assertEqual(millis_to_str(millis), str_)

    def test_millis_to_str_8(self):
        str_ = "10:24.172"
        millis = 624172
        self.assertEqual(millis_to_str(millis), str_)

class RaceTests(TestCase):

    def setUp(self):
        pass

    def test_insert_with_without_time(self):
        m = Map.objects.create(name='bla')
        p1 = Player.objects.create(username='asda', simplified='asda')
        p2 = Player.objects.create(username='asdb', simplified='asdb')
        p3 = Player.objects.create(username='asdc', simplified='asdc')
        p4 = Player.objects.create(username='asdd', simplified='asdd')
        race1 = Race.objects.create(player_id=p1.id, map_id=m.id)
        race2 = Race.objects.create(player_id=p2.id, map_id=m.id)
        race3 = Race.objects.create(player_id=p3.id, map_id=m.id)
        race4 = Race.objects.create(player_id=p4.id, map_id=m.id)
        race1.time = 12345
        race2.time = 54321
        race1.save()
        race2.save()

        self.assertEqual(len(Race.objects.filter(time__isnull=False)), 2)
        races = Race.objects.filter(map_id=m.id)
        completed_races = len([race for race in races if race.time is not None])
        self.assertEqual(completed_races, 2)