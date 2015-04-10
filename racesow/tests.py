"""
simple testcases, should be expanded for testing services.py

Usage (debian) from the /website directory:
    python manage.py test racesow
"""
import unittest
from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import (
    Map,
    Player,
    Race)
from racesow import models
from racesow import utils
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
        self.assertEqual(utils.millis_to_str(millis), str_)

    def test_millis_to_str_2(self):
        str_ = "9.986"
        millis = 9986
        self.assertEqual(utils.millis_to_str(millis), str_)

    def test_millis_to_str_3(self):
        str_ = "29.999"
        millis = 29999
        self.assertEqual(utils.millis_to_str(millis), str_)

    def test_millis_to_str_4(self):
        str_ = "59.999"
        millis = 59999
        self.assertEqual(utils.millis_to_str(millis), str_)

    def test_millis_to_str_5(self):
        str_ = "1:00.000"
        millis = 60000
        self.assertEqual(utils.millis_to_str(millis), str_)

    def test_millis_to_str_6(self):
        str_ = "1:00.001"
        millis = 60001
        self.assertEqual(utils.millis_to_str(millis), str_)

    def test_millis_to_str_7(self):
        str_ = "1:24.172"
        millis = 84172
        self.assertEqual(utils.millis_to_str(millis), str_)

    def test_millis_to_str_8(self):
        str_ = "10:24.172"
        millis = 624172
        self.assertEqual(utils.millis_to_str(millis), str_)


class NicknameTests(TestCase):
    def setUp(self):
        pass

    def test_nickname_1(self):
        name = u'|^^|GallotoroDBS^7'
        utils.username_with_html_colors(name)

    def test_nickname_2(self):
        name = u'^9|^1E^2R^3E^4N^^|^7'
        utils.username_with_html_colors(name)

    def test_nickname_3(self):
        name = u'^^Z[e]X^^^7'
        utils.username_with_html_colors(name)

    def test_nickname_4(self):
        name = u'^^.  ^4_  ^8.^7'
        utils.username_with_html_colors(name)

    def test_nickname_5(self):
        name = u'^^Laser^5pistole^7'
        utils.username_with_html_colors(name)

    def test_nickname_6(self):
        name = u'^^\'\'**^7'
        utils.username_with_html_colors(name)

    def test_nickname_7(self):
        name = u'^^&#39;&#39;**^7'
        utils.username_with_html_colors(name)

    def test_nickname_8(self):
        name = u'^9|^1E^2R^3E^4N^^|^7'
        utils.username_with_html_colors(name)


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


class APITagTests(APITestCase):
    """Test Tag API endpoint

    This serves as the test to ensure basic rest-framework functionality
    works as expected. Other endpoint tests should focus on endpoint specific
    functionality.
    """

    def setUp(self):
        self.user = User.objects.create_superuser(**cred)
        self.server = models.Server.objects.create(user=self.user)
        self.client.login(**cred)

        tags = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
                'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'foutreen',
                'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen',
                'twenty']
        models.Tag.objects.bulk_create([
            models.Tag(name=name) for name in tags
        ])

    def tearDown(self):
        self.client.logout()
        self.client.credentials()

    def test_list_get(self):
        """It should paginate and give the first few tags"""
        response = self.client.get(apiroot + '/tags/?page_size=10')
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(data['next'])
        self.assertFalse(data['previous'])
        self.assertEqual(data['count'], 20)
        self.assertEqual(len(data['results']), 10)

    def test_list_post(self):
        """It should return a new tag"""
        tagdata = {'name': 'new tag'}
        response = self.client.post(apiroot + '/tags/', tagdata, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, tagdata)
        self.assertTrue(models.Tag.objects.get(**tagdata))

    def test_list_sort(self):
        """It should sort by name"""
        response = self.client.get(apiroot + '/tags/')
        tags1 = response.data['results']

        response = self.client.get(apiroot + '/tags/?sort=-name')
        tags2 = response.data['results']

        self.assertEqual(tags1[::-1], tags2)

    def test_detail_get(self):
        """It should fetch a new tag"""
        response = self.client.get(apiroot + '/tags/one/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'name': 'one'})

    def test_detail_put(self):
        """It should update an existing tag"""
        tagdata = {'name': 'new tag'}
        response = self.client.put(
            apiroot + '/tags/one/',
            tagdata,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, tagdata)
        self.assertTrue(models.Tag.objects.get(**tagdata))
        with self.assertRaises(models.Tag.DoesNotExist):
            models.Tag.objects.get(name='one')

    def test_detail_patch(self):
        """It should update an existing tag"""
        tagdata = {'name': 'new tag'}
        response = self.client.patch(
            apiroot + '/tags/one/',
            tagdata,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, tagdata)
        self.assertTrue(models.Tag.objects.get(**tagdata))
        with self.assertRaises(models.Tag.DoesNotExist):
            models.Tag.objects.get(name='one')

    def test_detail_delete(self):
        """It should delete an existing tag"""
        response = self.client.delete(apiroot + '/tags/one/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(models.Tag.DoesNotExist):
            models.Tag.objects.get(name='one')


class APIMapTests(APITestCase):
    """Test Map API endpoint"""

    def setUp(self):
        self.user = User.objects.create_superuser(**cred)
        self.server = models.Server.objects.create(user=self.user)
        self.client.login(**cred)

        t1 = models.Tag.objects.create(name='one')
        t2 = models.Tag.objects.create(name='two')

        m1 = models.Map.objects.create(name='Map One')
        m2 = models.Map.objects.create(name='Map Two')
        models.Map.objects.create(name='Map Three')
        m1.tags.add(t1, t2)
        m2.tags.add(t1)

    def tearDown(self):
        self.client.logout()
        self.client.credentials()

    def test_list_regex(self):
        """It should filter on a name regex"""
        pattern = utils.b64encode('o$')
        response = self.client.get(apiroot + '/maps/?pattern=' + pattern)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Map Two')

    def test_list_tags(self):
        """It should return maps that contain specified tags"""
        # One map has both tags 'one' and 'two'
        tags = utils.jsonencode(['one', 'two'])
        response = self.client.get(apiroot + '/maps/?tags=' + tags)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

        # Two maps are tagged with 'one'
        tags = utils.jsonencode(['one'])
        response = self.client.get(apiroot + '/maps/?tags=' + tags)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    @unittest.expectedFailure
    def test_list_rand(self):
        """It should randomize the output order"""
        response = self.client.get(apiroot + '/maps/?rand')
        order1 = [m['name'] for m in response.data['results']]

        response = self.client.get(apiroot + '/maps/?rand')
        order2 = [m['name'] for m in response.data['results']]

        # This will fail with probability 1/6
        self.assertNotEqual(order1, order2)

    def test_detail_get(self):
        """It should lookup maps on b64 encoded name"""
        name = utils.b64encode('Map Two')
        response = self.client.get(apiroot + '/maps/' + name + '/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Map Two')


class APIPlayerTests(APITestCase):
    """Test Player API endpoint"""

    def setUp(self):
        self.user = User.objects.create_superuser(**cred)
        self.server = models.Server.objects.create(user=self.user)
        self.client.login(**cred)

        m1 = models.Map.objects.create(name='Map One')
        m2 = models.Map.objects.create(name='Map Two')

        p1 = models.Player.objects.create(username='P1', name='P1',
                                          simplified='P1')
        p2 = models.Player.objects.create(username='P2', name='P2',
                                          simplified='P2')

        models.Race.objects.create(player=p1, map=m1, time=1)
        models.Race.objects.create(player=p1, map=m2, time=2)
        models.Race.objects.create(player=p2, map=m1, time=3)

    def tearDown(self):
        self.client.logout()
        self.client.credentials()

    def test_list_simplified(self):
        """It should filter by simplified name"""
        n1 = utils.b64encode('P2')
        response = self.client.get(apiroot + '/players/?simplified=' + n1 +
                                   '/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['simplified'], 'P2')

    def test_detail_record(self):
        """It should attach a record if asked"""
        # No record field if mid not supplied
        n1 = utils.b64encode('P1')
        response = self.client.get(apiroot + '/players/' + n1 + '/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('record', response.data)

        # correct record if asked
        response = self.client.get(apiroot + '/players/' + n1 + '/?mid=1')
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['record']['player'], data['id'])
        self.assertEqual(data['record']['map'], 1)

        # null record if not found
        response = self.client.get(apiroot + '/players/' + n1 + '/?mid=8')
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['record'], None)
