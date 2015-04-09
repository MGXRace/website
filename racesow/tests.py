"""
simple testcases, should be expanded for testing services.py

Usage (debian) from the /website directory:
    python manage.py test racesow
"""
from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import (
    Map,
    Player,
    Race)
from racesow import models
from racesow.utils import millis_to_str, username_with_html_colors
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()
apiroot = '/drf'
cred = {
    'username': 'test',
    'email': None,
    'password': 'pass',
}


class MapMethodTests(TestCase):
    def setUp(self):
        # settings.configure()
        pass

    def test_get_existing_map(self):
        insert_name = "MyTestMap"
        map_ = Map()
        map_.name = insert_name
        map_.save()

        Map.objects.get(name=insert_name)

    def test_get_nonexisting_map(self):
        insert_name = "MyTestMap"
        select_name = "NotMyTestMap"
        map_ = Map()
        map_.name = insert_name
        map_.save()

        with self.assertRaises(Map.DoesNotExist):
            Map.objects.get(name=select_name)

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


class NicknameTests(TestCase):
    def setUp(self):
        pass

    def test_nickname_1(self):
        name = u'|^^|GallotoroDBS^7'
        username_with_html_colors(name)

    def test_nickname_2(self):
        name = u'^9|^1E^2R^3E^4N^^|^7'
        username_with_html_colors(name)

    def test_nickname_3(self):
        name = u'^^Z[e]X^^^7'
        username_with_html_colors(name)

    def test_nickname_4(self):
        name = u'^^.  ^4_  ^8.^7'
        username_with_html_colors(name)

    def test_nickname_5(self):
        name = u'^^Laser^5pistole^7'
        username_with_html_colors(name)

    def test_nickname_6(self):
        name = u'^^\'\'**^7'
        username_with_html_colors(name)

    def test_nickname_7(self):
        name = u'^^&#39;&#39;**^7'
        username_with_html_colors(name)

    def test_nickname_8(self):
        name = u'^9|^1E^2R^3E^4N^^|^7'
        username_with_html_colors(name)


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
        Race.objects.create(player_id=p3.id, map_id=m.id)
        Race.objects.create(player_id=p4.id, map_id=m.id)
        race1.time = 12345
        race2.time = 54321
        race1.save()
        race2.save()

        races = Race.objects.filter(time__isnull=False)
        self.assertEqual(len(races), 2)

        races = Race.objects.filter(map_id=m.id)
        completed_races = [race for race in races if race.time is not None]
        self.assertEqual(len(completed_races), 2)


class APIAuthTests(APITestCase):
    """Test API authentication"""

    def setUp(self):
        # Make an authenticated user / server to access the api
        self.user = User.objects.create_superuser(**cred)
        self.server = models.Server.objects.create(user=self.user)

    def tearDown(self):
        # Clear any saved credentials
        self.client.logout()
        self.client.credentials()

    def test_unauthorized(self):
        """Unauthorized requests are forbidden"""
        response = self.client.get(apiroot + '/players/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_tokenauth(self):
        """Token authorized requests are allowed"""
        key = self.user.auth_token.key
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + key)

        response = self.client.get(apiroot + '/players/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sessionauth(self):
        """Session authorized requests are allowed"""
        self.client.login(**cred)

        response = self.client.get(apiroot + '/players/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
