from django.db import models

# TODO views
#


_null = {'blank': True, 'null': True, 'default': None}

# MAP_DIR defined in TODO define it somewhere

PK3_STATUS = [
    'new',          # new pk3file detected in MAP_DIR
    'acceptance',   # pk3file is eligible for downloading by a special
                    # acceptance server
    'approved',     # pk3file is eligible for downloading by website visitors
                    # and all gameservers
    'rejected',     # pk3file is rejected (because of shader/texture errors)
    'replaced'      # pk3file is still rejected but a '-mgxfix' version has
                    # been created and linked to this one
]

# TODO include start/stoptimer checking
# https://github.com/hettoo/pk3check/blob/master/pk3check.pl#L181

# TODO auto create weapon tags
# https://github.com/MGXRace/utilities/blob/master/dbutils/pk3scan.py#L103


# TODO: in maps/racesow/ create a directory base/ containing base pk3files?
#

# TODO parse 'skyparms' command because this implicitly requires 6 .tga files
# http://www.heppler.com/shader/shader/section3.htm#3.1
#
# Example:
# dray2k_stairjump_p1/scripts/stratosphere.shader
#
# textures/stratosphere/strat_skybox
# {
#     skyparms env/stratosphere/stratosphere - -
# }
#
# references
# dray2k_stairjump_p1\env\stratosphere\stratosphere_bk.tga
# dray2k_stairjump_p1\env\stratosphere\stratosphere_dn.tga
# dray2k_stairjump_p1\env\stratosphere\stratosphere_ft.tga
# dray2k_stairjump_p1\env\stratosphere\stratosphere_lf.tga
# dray2k_stairjump_p1\env\stratosphere\stratosphere_rf.tga
# dray2k_stairjump_p1\env\stratosphere\stratosphere_up.tga
#


class Pk3file(models.Model):
    """Maps Pk3file Model

    A .pk3 file can be named differently than the .bsp file it contains,
    and it c

    Model Fields:
        filename (str): filename of .pk3 (including extension)
        filesize (int): size of .pk3 file in bytes
        md5hash (bytes): md5hash of the .pk3 content
        status (str): current validation status of .pk3 file
        badformat (bool): true for .pk3 files not in ZIP format
        base (bool): true for a basewsw's data_*.pk3 reference file (not a map)
        replaces (Pk3file): the rejected pk3file which is replaced by this
                            pk3file, or null
    """
    filename = models.CharField(max_length=64, unique=True)
    filesize = models.IntegerField(default=0)
    md5hash = models.BinaryField(max_length=16)
    status = models.CharField(max_length=16, choices=PK3_STATUS,
                              default=PK3_STATUS[0])
    badformat = models.BooleanField(default=False)
    base = models.BooleanField(default=False)
    replaces = models.ForeignKey('self', **_null)


class Bspfile(models.Model):
    """Maps Bspfile model

    The name of a .bsp file is how a map is identified in the scoreboard and
    ingame.

    Model Fields:
        pk3file (Pk3file): pk3file containing the .bsp file
        filename (str): filename of .bsp (excluding extension)
        md5hash (bytes): md5hash of the .bsp content
        shaders (RelatedManager): Manager for Shader objects associated with
                                  the .bsp file
    """
    pk3file = models.ForeignKey(Pk3file, blank=False)
    filename = models.CharField(max_length=64)
    md5hash = models.BinaryField(max_length=16)
    shaders = models.ManyToManyField(Shader)


class Levelshot(models.Model):
    """Maps Levelshot model

    Model Fields:
        pk3file (Pk3file): .pk3 file containing this levelshot
        filename (str): filename of levelshot (including extension)
    """
    pk3file = models.ForeignKey(Pk3file, blank=False)
    filename = models.CharField(max_length=64)


class Shader(models.Model):
    """Maps Shader model

    Some quotes from "Quake III Arena Shader Manual: 2.2 Shader Name &
    File Conventions". Mirror: http://www.heppler.com/shader


    "The first line is the shader name. Shader names can be up to 63
    characters long. The names are often a mirror of a pathname to a
    .tga file without the extension or basedir (/quake3/baseq3 in our
     case), but they do not need to be."

    "Shaders that are placed on surfaces in the map editor commonly mirror
    a .tga file, but the "qer_editorimage" shader parameter can force the
    editor to use an arbitrary image for display."

    "Shader pathnames have a case sensitivity issue - on windows, they
    aren't case sensitive, but on unix they are. Try to always use
    lowercase for filenames, and always use forward slashes '/' for
    directory separators.|

    Model Fields:
        pk3file (Pk3file): .pk3 file containing this shader definition
        name (str): name of the shader definition
        textures (RelatedManager): Manager for Texture objects affected
                                   by this shader definition
    """
    pk3file = models.ForeignKey(Pk3file, blank=False)
    name = models.CharField(max_length=64)
    textures = models.ManyToManyField(Texture)


class Texture(models.Model):
    """Maps Texture model

    Model Fields:
        pk3file (Pk3file): .pk3 file containing this texture
        filename (str): filename of texture (including extension)
        extension (str): filename extension

    """
    pk3file = models.ForeignKey(Pk3file, blank=False)
    filename = models.CharField(max_length=64)
    md5hash = models.BinaryField(max_length=16)
