import random
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from itertools import product
from faker import Faker
from racesow import models as mod


fake = Faker()


class Command(BaseCommand):
    help = 'Generate fake data for the racesow models'

    def __init__(self):
        super(Command, self).__init__()
        self.tags = None
        self.servers = None
        self.maps = None
        self.players = None
        self.races = None

    def checkSafe(self):
        """Ensure it is safe to perform this operation"""
        assert settings.DEBUG, 'This command should not be used in production'
        assert settings.DATABASES['default']['ENGINE'].endswith('sqlite3'), (
            'This command should only be used with an sqlite database'
        )

    def clean(self):
        """Drop all database rows"""
        mod.Checkpoint.objects.all().delete()
        mod.Race.objects.all().delete()
        mod.Map.objects.all().delete()
        mod.Player.objects.all().delete()
        mod.Tag.objects.all().delete()

    def fake_checkpoint(self, race, number):
        return mod.Checkpoint(
            race=race,
            number=number,
            time=random.randrange(1e9),
        )

    def fake_checkpoints(self):
        """Generate fake checkpoints"""
        self.checkpoints = []
        for race in self.races:
            count = range(random.randrange(10))
            self.checkpoints.extend([
                self.fake_checkpoint(race, n) for n in count
            ])
        mod.Checkpoint.objects.bulk_create(self.checkpoints)

    def fake_tag(self, count):
        """Generate up to N fake tags"""
        names = {word for word in fake.words(nb=count)}
        self.tags = [mod.Tag.objects.create(name=name) for name in names]

    def fake_player(self, name):
        return mod.Player.objects.create(
            username=name,
            admin=random.choice([True, False]),
            name=name,
            simplified=name,
            playtime=random.randrange(1e9),
            races=random.randrange(1e3),
            maps=random.randrange(1e3),
            maps_finished=random.randrange(1e3),
            points=random.randrange(1e3),
        )

    def fake_players(self, count):
        names = {fake.name() for _ in range(count)}
        self.players = [self.fake_player(name) for name in names]

    def fake_map(self, name):
        return mod.Map.objects.create(
            name=name,
            races=random.randrange(1e3),
            playtime=random.randrange(1e9),
            created=fake.date_time_this_century(),
            oneliner=fake.sentence(),
        )

    def fake_maps(self, count):
        names = {fake.name() for _ in range(count)}
        self.maps = [self.fake_map(name) for name in names]

        for m in self.maps:
            m.tags = random.sample(self.tags, random.randrange(8))

    def fake_race(self, player, map_, server):
        return mod.Race.objects.create(
            player=player,
            map=map_,
            server=server,
            time=random.randrange(1e9),
            playtime=random.randrange(1e9),
            points=random.randrange(40),
            rank=random.randrange(100),
            created=fake.date_time_this_century(),
            last_played=fake.date_time_this_century(),
        )

    def fake_races(self):
        self.races = []
        for map_, player in product(self.maps, self.players):
            if random.choice([True, False]):
                continue

            self.races.append(self.fake_race(player, map_, None))

    def handle(self, *args, **kwargs):
        """Main method for the command"""
        self.checkSafe()
        self.clean()

        self.fake_tag(20)
        self.fake_players(100)
        self.fake_maps(100)
        self.fake_races()
        self.fake_checkpoints()
