from maps.models import Pk3file

# TODO: in maps/racesow/ create directories base/ and levelshot/
MAP_DIR = ''  # path to map directory
BASE_DIR = ''  # path to base directory (data_xxx.pk3's and texture pk3's)
LEVELSHOT_DIR = ''  # path to levelshot directory


class Pk3Service:

    pk3file = None

    def __init__(self, pk3, base=False):
        """

        :param pk3: new or existing pk3 object
        :type pk3: str|file|Pk3file
        :param base: True for a base pk3, False for a map pk3
        """
        if type(pk3) == file:
            # new pk3 uploaded
            data = self._process_file(pk3, base)
            self.pk3file = self._register_pk3(data)
            self.evaluate()
        elif type(pk3) == Pk3file:
            # existing pk3
            self.pk3file = pk3
        elif type(pk3) == str:
            self.pk3file = Pk3file.objects.get(name=pk3)
        else:
            raise TypeError("Invalid argument passed to Pk3Service.__init__")

    # Private functions

    def _process_file(self, fileobj, base):
        file_content = {}
        # TODO validate file (check filename unique and/or mgxfix replacement, md5hash, etc), extract bspfiles/shaders/textures
        # TODO include start/stoptimer checking https://github.com/hettoo/pk3check/blob/master/pk3check.pl#L181
        return file_content

    def _register_pk3(self, data):
        """

        :param data: pk3file details, included bspfiles/shaders/textures
        :return: Pk3file entry
        """
        result = Pk3file()
        # TODO create all required db entries for the pk3
        # TODO create weapon tags for each bsp https://github.com/MGXRace/utilities/blob/master/dbutils/pk3scan.py#L103
        return result

    # Public functions

    def evaluate(self):
        """

        :param pk3file:
        :return:
        """
        # TODO depending on its status, evaluate the pk3's dependencies
        pass

    def approve(self):
        # TODO perform necessary actions for approving a pk3file
        pass

    def reject(self, disable=False):
        # TODO perform necessary actions for rejecting/disabling a pk3file
        pass

    def replace(self, pk3_to_replace):
        # TODO perform necessary actions to replace the specified Pk3file with the one stored in this Pk3Service object
        pass
