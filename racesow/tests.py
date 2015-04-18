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


class RSAPITest(object):
    """Mixin to provide sample data for API Tests"""

    def setUp(self):
        self.user = User.objects.create_superuser(**cred)
        self.server = models.Server.objects.create(user=self.user)
        self.client.login(**cred)

        tags = [
            {'name': 'strafe'},
            {'name': 'rocket'},
            {'name': 'plasma'},
            {'name': 'freestyle'},
            {'name': 'length:medium'},
        ]
        self.tags = [models.Tag.objects.create(**d) for d in tags]

        maps = [
            {'name': 'coldrun'},
            {'name': '0ups_beta2a'},
            {'name': 'gpl-arcaon'},
            {'name': 'pornstar-slopin'},
            {'name': 'gu3#8-bomb'},
        ]
        self.maps = [models.Map.objects.create(**d) for d in maps]

        map_tags = [
            [1],
            [3],
            [0, 4],
            [0, 4],
            [2, 4],
        ]
        for map_, tagset in zip(self.maps, map_tags):
            map_.tags = [self.tags[i] for i in tagset]

        players = [
            {
                'username': 'ale',
                'admin': True,
                'name': 'o^0_^7O a^9l^0e^7',
                'simplified': 'o_O ale',
            },
            {
                'username': 'murk',
                'admin': True,
                'name': 'murk',
                'simplified': 'murk',
            },
            {
                'username': 'pink',
                'admin': True,
                'name': '^9sjn^0|^4Pink',
                'simplified': 'sjn|Pink',
            },
            {
                'username': 'karl',
                'admin': True,
                'name': 'o^2_^7O ka^2r^7l^7',
                'simplified': 'o_O karl',
            },
        ]
        self.players = [models.Player.objects.create(**d) for d in players]

        races = [
            [ # ale
                {
                    'map': 0,
                    'time': 11943,
                },
                {
                    'map': 2,
                    'time': 29177,
                },
                {
                    'map': 3,
                    'time': None,
                },
            ],
            [ # murk
                {
                    'map': 0,
                    'time': 15728,
                },
                {
                    'map': 2,
                    'time': None,
                },
            ],
            [ # pink
                {
                    'map': 0,
                    'time': 17482,
                },
                {
                    'map': 2,
                    'time': 48271,
                },
                {
                    'map': 3,
                    'time': 12347,
                },
            ],
            [ # karl
            ],
        ]
        self.races = []
        for player, race_set in zip(self.players, races):
            for race in race_set:
                race['map'] = self.maps[race['map']]
                race['player'] = player
                self.races.append(models.Race.objects.create(**race))

        checkpoints = [
            [(0, 1234), (2, 2456), (4, 5678)],
            [(1, 3869)],
            [],
            [],
            [],
            [(2, 1234), (1, 2456), (0, 5678)],
            [(2, 2456)],
            [(1, 1234), (2, 2456)],
        ]
        self.checkpoints = []
        for race, checkpoint_set in zip(self.races, checkpoints):
            self.checkpoints.extend([
                models.Checkpoint.objects.create(race=race, number=n, time=t)
                for n, t in checkpoint_set
            ])

    def tearDown(self):
        self.client.logout()
        self.client.credentials()


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


class APITagTests(RSAPITest, APITestCase):
    """Test Tag API endpoint

    This serves as the test to ensure basic rest-framework functionality
    works as expected. Other endpoint tests should focus on endpoint specific
    functionality.
    """

    def test_list_get(self):
        """It should paginate and give the first few tags"""
        response = self.client.get(apiroot + '/tags/?page_size=3')
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(data['next'])
        self.assertFalse(data['previous'])
        self.assertEqual(data['count'], len(self.tags))
        self.assertEqual(len(data['results']), 3)

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
        name = self.tags[0].name
        response = self.client.get('{0}/tags/{1}/'.format(apiroot, name))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'name': name})

    def test_detail_put(self):
        """It should update an existing tag"""
        oldname = self.tags[0].name
        tagdata = {'name': 'new tag'}
        response = self.client.put(
            '{0}/tags/{1}/'.format(apiroot, oldname),
            tagdata,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, tagdata)
        self.assertTrue(models.Tag.objects.get(**tagdata))
        with self.assertRaises(models.Tag.DoesNotExist):
            models.Tag.objects.get(name=oldname)

    def test_detail_patch(self):
        """It should update an existing tag"""
        oldname = self.tags[0].name
        tagdata = {'name': 'new tag'}
        response = self.client.patch(
            '{0}/tags/{1}/'.format(apiroot, oldname),
            tagdata,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, tagdata)
        self.assertTrue(models.Tag.objects.get(**tagdata))
        with self.assertRaises(models.Tag.DoesNotExist):
            models.Tag.objects.get(name=oldname)

    def test_detail_delete(self):
        """It should delete an existing tag"""
        name = self.tags[0].name
        response = self.client.delete('{0}/tags/{1}/'.format(apiroot, name))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(models.Tag.DoesNotExist):
            models.Tag.objects.get(name=name)


class APIMapTests(RSAPITest, APITestCase):
    """Test Map API endpoint"""

    def test_list_regex(self):
        """It should filter on a name regex"""
        response = self.client.get(
            '{0}/maps/?pattern={1}'.format(apiroot, utils.b64encode('n$'))
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        self.assertEqual(response.data['results'][0]['name'], 'coldrun')

    def test_list_tags(self):
        """It should return maps that contain specified tags"""
        # Two maps have both tags 'strafe' and 'length:medium'
        tags = utils.jsonencode(['strafe', 'length:medium'])
        response = self.client.get('{0}/maps/?tags={1}'.format(apiroot, tags))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

        # Three maps are tagged with 'length:medium'
        tags = utils.jsonencode(['length:medium'])
        response = self.client.get(apiroot + '/maps/?tags=' + tags)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    @unittest.expectedFailure
    def test_list_rand(self):
        """It should randomize the output order"""
        response = self.client.get(apiroot + '/maps/?rand')
        order1 = [m['name'] for m in response.data['results']]

        response = self.client.get(apiroot + '/maps/?rand')
        order2 = [m['name'] for m in response.data['results']]

        # This will fail with probability 1/len(self.maps)
        self.assertNotEqual(order1, order2)

    def test_detail_get(self):
        """It should lookup maps on b64 encoded name"""
        name = utils.b64encode('coldrun')
        response = self.client.get('{0}/maps/{1}/'.format(apiroot, name))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'coldrun')

    def test_detail_record(self):
        """It should attach the best race if asked"""
        # Record field does not exist if not requested
        name = utils.b64encode('coldrun')
        response = self.client.get('{0}/maps/{1}/'.format(
            apiroot, name
        ))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('record', response.data)

        # Correct record returned if requested
        name = utils.b64encode('coldrun')
        response = self.client.get('{0}/maps/{1}/?record'.format(
            apiroot, name
        ))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['record']['time'], 11943)

        # Record is null if not found
        name = utils.b64encode('0ups_beta2a')
        response = self.client.get('{0}/maps/{1}/?record'.format(
            apiroot, name
        ))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data['record'])


class APIPlayerTests(RSAPITest, APITestCase):
    """Test Player API endpoint"""

    def test_list_simplified(self):
        """It should filter by simplified name"""
        response = self.client.get('{0}/players/?simplified={1}'.format(
            apiroot, utils.b64encode('o_O ale')
        ))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['simplified'], 'o_O ale')

    def test_detail_record(self):
        """It should attach a record if asked"""
        # No record field if mid not supplied
        response = self.client.get('{0}/players/{1}/'.format(
            apiroot, utils.b64encode('ale'), self.maps[0].pk
        ))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('record', response.data)

        # correct record if asked
        response = self.client.get('{0}/players/{1}/?mid={2}'.format(
            apiroot, utils.b64encode('ale'), self.maps[0].pk
        ))
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['record']['player']['simplified'], 'o_O ale')
        self.assertEqual(data['record']['map'], self.maps[0].pk)

        # null record if not found
        response = self.client.get('{0}/players/{1}/?mid={2}'.format(
            apiroot, utils.b64encode('ale'), self.maps[1].pk
        ))
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['record'], None)


class APIRaceTests(RSAPITest, APITestCase):
    """Test Race API endpoint"""

    def test_list_filter(self):
        """It should filter by map pk and player pk"""
        response = self.client.get('{0}/races/?map={1}'.format(
            apiroot, self.maps[0].pk
        ))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

        response = self.client.get('{0}/races/?map={1}&player={2}'.format(
            apiroot, self.maps[0].pk, self.players[0].pk
        ))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_detail_checkpoint(self):
        """It should attach checkpoints if they exist"""
        response = self.client.get('{0}/races/{1}/'.format(
            apiroot, self.races[0].pk
        ))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['checkpoints']), 3)
