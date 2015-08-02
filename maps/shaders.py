import re
from zipfile import ZipExtFile

BLOCK_OPEN = u"{"
BLOCK_CLOSE = u"}"
LINE_COMMENT = u"//"


# textures implicitly required for a skybox
SKYBOX_ELTS = [
    '_bk.tga',
    '_dn.tga',
    '_ft.tga',
    '_lf.tga',
    '_rf.tga',
    '_up.tga',
]


# matches skybox names in keywords
tex_filter_sky = re.compile('skyparms ((?:\S+/)+[^ ]+)', re.I | re.M)
# matches texture references in stages
tex_filter_stage = re.compile('((?:\S+/)+[^ ]+\.(?:tga|jpg))', re.I | re.M)


class InitializedError(Exception):
    pass


class EmptyShaderFile(Exception):
    pass


class BadShaderFormat(Exception):
    pass


def _sanitize(text):
    """remove commented line parts, strip whitespaces/tabs, omit empty lines"""
    return filter(None, [line.split(LINE_COMMENT)[0].strip() for line in text.splitlines()])


class ShaderFileParser(object):
    """Parses the input shader into a dictionary of the form:

    shaders = {
        "shader1_name": (
            ["shader1_keyline1", "shader1_keyline2", ...],
            [
                ["shader1_stage1_line1", "shader1_stage1_line2", ...],
                ["shader1_stage2_line1", ...]
            ]
        ),
        "shader2_name": (
            ["shader2_keyline1", "shader2_keyline2", "shader2_keyline3", ...],
            []
        )
    }
    """

    def __init__(self, _input):
        if type(_input) == file or type(_input) == ZipExtFile:
            _input = _input.read()
        elif not (type(_input) == unicode or type(_input) == str):
            raise TypeError("String or file input required.")
        self._shaders = None
        self._shaderfile = u"\n".join(_sanitize(_input))
        self._parse_shaderfile()

    def _check_initialized(self):
        if not self._shaders:
            raise InitializedError("The object has not been initialized properly")

    def _parse_shader(self, pos):
        """parsing a shader in a shaderfile, the pos param indicates the offset"""
        keylines = []
        stages = []
        next_block_open = self._shaderfile.find(BLOCK_OPEN, pos)     # find next shader/stage block start
        next_block_close = self._shaderfile.find(BLOCK_CLOSE, pos)    # find next shader/stage block close

        if next_block_close == -1:
            raise BadShaderFormat("There are more {'s than }'s")  # just checking!

        if next_block_open == -1:
            # there happen to be no stages in this shader and no next shader in this file, parse lines and return
            return next_block_close + 1, (_sanitize(self._shaderfile[pos:next_block_close]), [])

        while next_block_open < next_block_close:
            # parse keywords in between stages
            keylines.extend(_sanitize(self._shaderfile[pos:next_block_open]))
    
            # detect unsupported nesting of stages
            future_block_open = self._shaderfile.find(BLOCK_OPEN, next_block_open + 1)
            if future_block_open != -1 and future_block_open < next_block_close:
                raise BadShaderFormat(
                    "Detected nested stage at position {} (sanitized text), exiting.".format(future_block_open))
    
            # a stage is opened
            stages.append(_sanitize(self._shaderfile[next_block_open + 1:next_block_close]))
            pos = next_block_close + 1  # change position to after the stage-closing }
            next_block_open = self._shaderfile.find(BLOCK_OPEN, pos)     # find next shader/stage block start
            next_block_close = self._shaderfile.find(BLOCK_CLOSE, pos)    # find next shader/stage block close
    
            if next_block_close == -1:
                raise BadShaderFormat("There are more {'s than }'s")  # just checking!
    
            if next_block_open == -1:
                # no more stages in this shader and no next shader in this file
                break

        # parse keywords before/after stages
        keylines.extend(_sanitize(self._shaderfile[pos:next_block_close]))
        # return position to after the shader-closing }
        return next_block_close + 1, (keylines, stages)
    
    def _parse_shaderfile(self):
        self._shaders = {}
        pos = 0
        while pos < len(self._shaderfile):
            next_shader_start = self._shaderfile.find(BLOCK_OPEN, pos)
            if next_shader_start == -1:
                if pos == 0:
                    raise EmptyShaderFile("No shader definitions found")
                break  # reached end of file with trailing characters
            name_lines = _sanitize(self._shaderfile[pos:next_shader_start])
            if len(name_lines) != 1:
                raise BadShaderFormat(
                    "(pos {}, next {}): found {} line(s) before a shader definition, expected 1 line.".format(
                        pos, next_shader_start, len(name_lines)))
            pos, self._shaders[name_lines[0]] = self._parse_shader(next_shader_start + 1)

    def pretty_print(self):
        self._check_initialized()
        for name, shader in self._shaders.iteritems():
            print "{}".format(name)
            print "{"
            if len(shader) == 2:
                for i in shader[0]:
                    print "\t{}".format(i)
                for j in shader[1]:
                    print "\t{"
                    print "\t\t" + "\n\t\t".join(j)
                    print "\t}"
            print "}\n"

    def get_shaders(self):
        self._check_initialized()
        return self._shaders

    def get_texture_requirements(self):
        self._check_initialized()
        texture_requirements = {}
        for name, shader in self._shaders.iteritems():
            if len(shader) != 2:
                continue

            # the only requirements outside of stages are skybox textures, other textures are only for use in map editors
            texture_requirements[name] = set([
                tex_filter_sky.match(x).group(1) + y  # generate the 6 skybox .tga strings
                for x in filter(tex_filter_sky.match, shader[0])
                for y in SKYBOX_ELTS
            ])

            # get all texture requirements from all stages
            if shader[1]:
                texture_requirements[name].update(
                    sum([tex_filter_stage.findall(stageline) for stagelist in shader[1] for stageline in stagelist], [])
                )
        return texture_requirements
