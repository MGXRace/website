from django.db import models

_null = {'blank': True, 'null': True, 'default': None}


class Pk3file(models.Model):
    """Maps Pk3file Model

    A .pk3 file can be named differently than the .bsp file it contains,
    and it may contain multiple .bsp files.

    Model Fields:
        filename (str): filename of .pk3 (including extension). Not a unique
            field because entries of rejected Pk3files are kept for their md5hash
        filesize (int): size of .pk3 file in bytes
        md5hash (str): md5hash of the .pk3 content, unique field
        status (str): current validation status of .pk3 file
        base (bool): true for a basewsw's data_*.pk3 or mgx texturepack file (not a map)
        replaces (Pk3file): the pk3file which is superseded by this
                            pk3file, or null
        comments (str): precisely that
        created (datetime): datetime when pk3file was added to database
        updated (datetime): datetime when database entry was last updated
    """

    NEW = 'N'
    TESTING = 'T'
    OK = 'O'
    REJECTED = 'R'
    DISABLED = 'D'
    MGXFIX = 'M'

    VALID_STATUS_TRANSITIONS = {
        NEW: [TESTING, OK, REJECTED, MGXFIX],
        TESTING: [OK, REJECTED, MGXFIX],
        OK: [DISABLED],
        REJECTED: [MGXFIX],
        DISABLED: [MGXFIX],
        MGXFIX: [],
    }

    STATUS_CHOICES = (
        (NEW, 'New'),           # new pk3file detected in MAP_DIR
        (TESTING, 'Testing'),   # pk3file is eligible for downloading by a special acceptance server
        (OK, 'Ok'),             # pk3file is eligible for downloading by website visitors and all gameservers
        (REJECTED, 'Rejected'), # pk3file is rejected (has not been placed on server, file itself is removed)
        (DISABLED, 'Disabled'), # pk3file is disabled (has been placed on server and may have been downloaded)
        (MGXFIX, 'Mgxfix'),     # pk3file is still disabled/rejected but a '-mgxfix' version has been created and
                                # linked to this one
    )

    filename = models.CharField(max_length=64)
    filesize = models.IntegerField(default=0)
    md5hash = models.CharField(max_length=16, unique=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=NEW)
    base = models.BooleanField(default=False)
    replaces = models.ForeignKey('self', **_null)
    comments = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __init__(self, *args, **kwargs):
        super(Pk3file, self).__init__(*args, **kwargs)
        self._old_status = self.status if self.pk else None  # store the current status for an existing entry

    def save(self, *args, **kwargs):
        # Validate status transition
        if self._old_status and self._old_status != self.status:
            if self.status not in self.VALID_STATUS_TRANSITIONS[self._old_status]:
                raise ValueError("Updating pk3file status {} to status {} is not allowed".format(
                    self._old_status, self.status))
        super(Pk3file, self).save(*args, **kwargs)  # call the "real" save() method


class Bspfile(models.Model):
    """Maps Bspfile model

    The name of a .bsp file is how a map is identified in the scoreboard and ingame.

    Model Fields:
        pk3file (Pk3file): pk3file containing the .bsp file
        filename (str): filename of .bsp (excluding extension)
        md5hash (str): md5hash of the .bsp
        created (datetime): datetime when bspfile was added to database
    """
    pk3file = models.ForeignKey(Pk3file)
    filename = models.CharField(max_length=64)
    md5hash = models.CharField(max_length=16)
    created = models.DateTimeField(auto_now_add=True)


class Levelshot(models.Model):
    """Maps Levelshot model

    Model Fields:
        pk3file (Pk3file): .pk3 file containing this levelshot
        filename (str): filename of levelshot (including extension)
    """
    pk3file = models.ForeignKey(Pk3file)
    filename = models.CharField(max_length=64)
    # TODO couple with bspfile ?


class Texture(models.Model):
    """Maps Texture model

    Model Fields:
        filename (str): filename of texture (full path excluding extension)
        extension (str): filename extension
        md5hash (str): md5hash of the texture file
        pk3file (Pk3file): .pk3 file containing this texture
        created (datetime): datetime when texture was added to database
    """
    filename = models.CharField(max_length=64)
    extension = models.CharField(max_length=4)
    md5hash = models.CharField(max_length=16)
    pk3file = models.ForeignKey(Pk3file)
    created = models.DateTimeField(auto_now_add=True)


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
    directory separators.

    Model Fields:
        name (str): name of the shader definition
        pk3file (Pk3file): .pk3 file containing this shader definition
        created (datetime): datetime when shader was added to database
    """
    name = models.CharField(max_length=64)
    pk3file = models.ForeignKey(Pk3file)
    created = models.DateTimeField(auto_now_add=True)


class BspReq(models.Model):
    """Maps BspRequirement model

    This model represents a shader/texture referenced from (hence a requirement for) a bspfile.

    Model Fields:
        name (str): full reference string
        pk3file (Pk3file): Pk3file containing the bspfile
        bspfile (Bspfile): Bspfile containing the reference
        created (datetime): datetime when reference was added to database
    """
    name = models.CharField(max_length=64)
    pk3file = models.ForeignKey(Pk3file)
    bspfile = models.ForeignKey(Bspfile)
    created = models.DateTimeField(auto_now_add=True)


class ShaderReq(models.Model):
    """Maps ShaderRequirement model

    This model represents a texture referenced from (hence a requirement for) a shader.

    Model Fields:
        filename (str): filename of referenced texture (full path excluding extension)
        extension (str): filename extension
        pk3file (Pk3file): Pk3file containing the shader
        created (datetime): datetime when reference was added to database
    """
    filename = models.CharField(max_length=64)
    extension = models.CharField(max_length=4)
    pk3file = models.ForeignKey(Pk3file)
    created = models.DateTimeField(auto_now_add=True)
